from decimal import Decimal
from time import sleep
from datetime import datetime
from json import load
from ccxt import kucoin
from threading import Thread, Event
from traceback import print_exc
from os import system
from ccxt.base.errors import NetworkError
from random import choice
class TradingBot:

	def __init__(self, client_obj, conf_file):
		with open(conf_file, "r") as f:
			d = load(f)
		self.c = client_obj
		self.take_profit = Decimal(d["take_profit"])
		self.qty = Decimal(d["quantity"])
		self.asset = d["asset"] 
		self.base_asset = d["base_asset"]
		self.pair = self.asset + "/" +self.base_asset
		self.refresh_rate = d["refresh_rate"]
		self.log_file = d["log_file"]
		self.trade_min = (d["trade_min"])
		self.trade_max = (d["trade_max"])
		self.cooldown = (d["cooldown"])
		self.config_file = conf_file
		self.precison = d["precison"]
		self.taker_fee = Decimal(d["taker_fee"])
		self.maker_fee = Decimal(d["maker_fee"])
		self.logging_enabled = d["logging_enabled"]
		self.gas = Decimal(d["kcs_for_gas"])
		self.gas_up_enabled = d["buy_kcs_automatically"]
		self.ttp = d["trailing_take_profit_enabled"]
		self.trailing_deviation = d["trailing_deviation"]
		self.banner_dir_path = d["banner_folder_path"]
		#instance vars that need to be persistent through config updates go here
		self.last_sell_id, self.name, self.start_time = "", "", ""
		self.num_buys, self.num_sells, self.total_gains, self.potential_gain = 0, 0, 0, 0
		self.event = Event()

	def log(self, x):
		if self.logging_enabled:
			d = datetime.now()
			timestamp = d.strftime("%m/%d/%Y %H:%M:%S")
			with open(self.log_file, "a") as f:
				f.write(f"[{timestamp}] {x}")

	def updateConfig(self):
		tmp = [self.last_sell_id, self.num_sells, self.num_buys, self.total_gains, self.potential_gain, self.name, self.start_time, self.event]
		self.__init__(self.c, self.config_file)
		self.last_sell_id = tmp[0]
		self.num_sells = tmp[1]
		self.num_buys = tmp[2]
		self.total_gains = tmp[3]
		self.potential_gain = tmp[4]
		self.name = tmp[5]
		self.start_time = tmp[6]
		self.event = tmp[7]
		self.log("[INFO] Config updated\n")

	def gasUp(self):
		#self.gas -- represents the number to compare to KCS balance to see if balance is too low and the quantity of KCS to buy.
		if Decimal(self.c.fetchBalance()["KCS"]["free"]) < Decimal(self.gas) and self.gas_up_enabled:
			self.log("[WARNING] KCS balance is too low to pay for maker or taker fees. Attempting to trade for more...\n")
			buy_ord = self.c.createMarketBuyOrder("KCS/BTC", self.gas)
			self.log(f'[INFO] {buy_ord["amount"]} KCS bought.\n')

	def mkSellPrice(self, buy_price, percent_profit): # ((gain_offset + fee_offset) * buy_price) + buy_price
		return ((((percent_profit/Decimal(100))+((self.maker_fee+self.taker_fee)/Decimal(100)))*buy_price)+buy_price)

	def profitLoss(self, buy_price, sell_price, qty): # (sell_price - buy_price) * qty
		return ((Decimal(sell_price) - Decimal(buy_price))*(Decimal(qty)))

	def stripTradeStruct(self, _id):
		x = self.c.fetchOrder(_id)
		return {"price" : Decimal(x["price"]), "amount" : Decimal(x["amount"])}

	def tick(self):
		price = Decimal(self.c.fetchTicker(self.pair)["last"])# defined for one execution cycle
		if (not self.c.fetchOpenOrders(self.pair)):
			if self.last_sell_id:
				sell_order = self.stripTradeStruct(self.last_sell_id)
				self.num_sells += 1
				self.total_gains += self.potential_gain
				self.last_sell_id = ""
				self.potential_gain = 0
				self.log(f"[INFO] Sell order for {round(sell_order['amount'], 8)} {self.asset} at {round(sell_order['price'], 8)} {self.base_asset} filled.\n")
				self.log(f"[INFO] Entering {self.cooldown} second cooldown.\n")
				self.event.wait(self.cooldown)
			elif (self.trade_min<=price<=self.trade_max):
				self.gasUp()
				buy_ord = self.c.createMarketBuyOrder(self.pair, self.qty)
				buy_price = self.stripTradeStruct(buy_ord["id"])["price"]
				sell_price = self.mkSellPrice(buy_price, self.take_profit)
				self.log(f"[INFO] Bought {round(self.stripTradeStruct(buy_ord['id'])['amount'], 8)} {self.asset} for {round(buy_price, 8)} {self.base_asset}. Order Id: {buy_ord['id']}\n")
				self.num_buys += 1
				sleep(0.2)
				assert self.profitLoss(buy_price, sell_price, self.qty) > 0
				self.potential_gain = (self.profitLoss(buy_price, sell_price, self.qty))
				sell_ord = self.c.createLimitSellOrder(self.pair, round(self.qty, 8), round(sell_price, self.precison))
				self.last_sell_id = sell_ord["id"]
				self.log(f"[INFO] Posted limit-sell order for {round(self.qty, 8)} {self.asset} at {round(sell_price, 8)} {self.base_asset}.\n")

	def run(self):
		def logError(msg, fname):
			self.log(f"[ERROR] {msg}.\n")
			with open(fname, "w") as f:
				print_exc(file=f)
		self.log("[INFO] Bot started. Using configuration file \"{0}\"".format(self.config_file)+"\n")
		self.log(f"[INFO] Base asset balance: {self.c.fetchBalance()[self.base_asset]['free']} {self.base_asset}\n")
		while not self.event.is_set():
			try:
				self.tick()
				self.event.wait(self.refresh_rate)
			except NetworkError:
				logError("NetworkError occured.", "error_network_error.txt")
			except Exception:
				logError("Other error occured.", "error_other.txt")
				break
		self.log("[INFO] Status dump----------\n")
		self.log(f"Buys: {self.num_buys}\n")
		self.log(f"Sells: {self.num_sells}\n")
		self.log(f"Total estimated gains: {round(self.total_gains, 8)}\n")
		self.log("[INFO] Bot Stopped\n")

	def stop(self):
		self.event.set()

class Interface:

	def __init__(self, api, api_secret, passphrase):
		self.threads, self.bot_instances = [], []
		self.clock_sync_interval = 60.0 # interpreted as minutes
		self.clock_sync_event = Event()
		self.client = kucoin({"apiKey" : api, "secret" : api_secret, "password" : passphrase})

	def createThread(self, fnct, name_of_thread, start_on_creation=False, d=False): #returns position of created thread
		self.threads.append(Thread(target=fnct, daemon=d, name=name_of_thread))
		if start_on_creation:
			self.threads[(len(self.threads)-1)].start()
		return len(self.threads)-1

	def removeThread(self, i): # removeThread and startThread both return true if the respective function was able to succeed in its task
		if not self.threads[i].is_alive():
			self.threads.remove(self.threads[i])
			return True
		else:return False

	def startThread(self, i):
		if not self.threads[i].is_alive():
			self.threads[i].start()
			return True
		else:return False

	def stopClockSyncTask(self):
		self.clock_sync_event.set()

	def ntpSync(self):
		while True:
			if self.clock_sync_event.is_set():
				break
			system("echo xxxxxxxx | sudo -S service ntp stop && echo xxxxxxxx | sudo -S ntpd -gq > /dev/null && echo xxxxxxxx | sudo -S service ntp start")
			self.clock_sync_event.wait(self.clock_sync_interval*60) # convert to minutes

	def createNewBot(self, config_file, _name, run_on_creation=False): # NAMES CANNOT BE THE SAME!!!!!!
		x = TradingBot(self.client, config_file)#change depending on subclass
		x.name = _name
		pos = self.createThread(x.run,  _name, start_on_creation=run_on_creation, d=True)
		self.bot_instances.append([x, pos])

	def findBot(self, n):
		return int([self.bot_instances.index(i) for i in self.bot_instances if i[0].name == n][0])

	def status(self):
		if self.threads:
			print("----------Worker Thread Status----------")
			for i in self.threads:
				print(f"Name: {i.name}", end=" | ")
				print(f"Status: {('Running' if i.is_alive() else 'Stopped')}")
		else:
			print("No worker threads created")

	def makeReport(self, fname, i):
		runtime = None
		with open(fname, "w") as f:
			with open(choice(["banners/banner1.txt", "banners/banner2.txt", "banners/banner3.txt"]), "r") as x:
				for ln in x:
					f.write(ln)       
			f.write("\nTime of generation: {0}\n".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
			try:runtime = datetime.now()-self.bot_instances[i][0].start_time
			except:pass
			f.write(f"Runtime: {runtime} (h:m:s:ms)\n")
			f.write("Buys executed: {0}\nSells executed: {1}\n".format(self.bot_instances[i][0].num_buys, self.bot_instances[i][0].num_sells))
			f.write("Current return per trade: {0} {1}\n".format((f'{(self.bot_instances[i][0].potential_gain):.8f}'), self.bot_instances[i][0].base_asset))
			f.write("Total estimated gains: {0} {1}\n\n".format((f'{(self.bot_instances[i][0].total_gains):.8f}'), self.bot_instances[i][0].base_asset))
			f.write("-----Contents of \"{0}\" at time of report generation------\n".format(self.bot_instances[i][0].config_file))
			with open(self.bot_instances[i][0].config_file, "r") as y:
				for i in y:
					f.write(i)
					
	def main(self):
		usr_in = input("/BotInterface/--> ")
		if usr_in == "status":
			self.status()
			self.main()
		elif usr_in == "start bot":
			bot = input("Enter name of bot to start: ")
			self.bot_instances[self.findBot(bot)][0].start_time = datetime.now()
			self.threads[self.bot_instances[self.findBot(bot)][1]].start()
			self.main()
		elif usr_in == "start all":
			for i in self.bot_instances:i[0].start_time = datetime.now()
			for i in self.threads:
				if i.name != "clock_sync":
					self.startThread(self.threads.index(i))
					sleep(5)
			self.main()
		elif usr_in == "help":
			print("start bot\nstart all\nstop all\nstart ntp_sync\nstop ntp_sync\nset sync_interval\ngenerate bot report\ngenerate all\ncreate bot\nstop bot\nstop all\nupdate bot config\nupdate all\nquit")
			self.main()
		elif usr_in == "start ntp_sync":
			self.createThread(self.ntpSync, "clock_sync", start_on_creation=True, d=True)
			self.main()
		elif usr_in == "stop ntp_sync":
			self.stopClockSyncTask()
			self.main()
		elif usr_in == "set sync_interval":
			self.clock_sync_interval = float(input("Enter new interval in minutes: "))
			self.main()
		elif usr_in == "create bot":
			name = input("Enter a name for the new bot: ")
			config_file = input("Enter name of the configuration file to use: ")
			self.createNewBot(config_file, name)
			self.main()
		elif usr_in == "stop bot":
			bot = input("Enter name of bot to stop: ")
			self.bot_instances[self.findBot(bot)][0].stop()
			self.main()
		elif usr_in == "stop all":
			for i in self.bot_instances:i[0].stop()
			self.main()
		elif usr_in == "update bot config":
			bot = input("Enter name of bot to update: ")
			self.bot_instances[self.findBot(bot)][0].updateConfig()
			self.main()
		elif usr_in == "update all":
			for i in self.bot_instances:i[0].updateConfig()
			self.main()
		elif usr_in == "generate bot report":
			bot = input("Enter name of bot: ")
			pos = self.findBot(bot)
			self.makeReport(self.bot_instances[pos][0].name+".txt", pos)
			self.main()
		elif usr_in == "generate all":
			for i in self.bot_instances:self.makeReport(i[0].name+".txt", self.bot_instances.index(i))
			self.main()
		elif usr_in == "exit" or usr_in == "quit":
			if not self.threads and not self.bot_instances:
				exit(0)
			else:
				exitflag = None
				for i in self.threads:
					if i.is_alive():
						exitflag = False
					else:
						self.removeThread(self.threads.index(i))
				if exitflag == False:
					print("One or more threads are still alive")
					self.main()
				else:
					exit(0)
		else:
			print("Unrecognized command")
			self.main()