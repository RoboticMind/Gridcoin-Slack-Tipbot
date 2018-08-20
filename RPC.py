import requests
import json
from Slack_Connection import *
from decimal import *
from fractions import *
def get_balances_json():
	global main_json
	with open("Users.json", "r") as file:
		temp = file.read()
		temp = json.loads(temp)
		main_json = temp

def find_user_attribute(user_id,type):
	global main_json
	get_balances_json()
	for x in range(0,len(main_json["Users"])):
		if main_json["Users"][x]["User_ID"] == user_id:
			return_value = main_json["Users"][x][type]
	if "return_value" in locals():
		return return_value
	else:
		return None

def RPC_call(method, params):
	url="http://127.0.0.1:8832/"
	with open("Config/Username&Password.txt") as file:
		information = file.read().splitlines()
		rpcuser = information[0]
		rpcpassword = information[1]
	if len(params) > 0:
		if type(params) == str:		
			payload = json.dumps({"jsonrpc":1.0,"method": method, "params": [params],"id":"test"})
		else:
			payload = json.dumps({"jsonrpc":1.0,"method": method, "params": params,"id":"test"})
	else:
		payload = json.dumps({"jsonrpc":1.0,"method": method,"id":"test"})
	headers = {'content-type': "text/plain", 'cache-control': "no-cache"}
	request_one = requests.Session()
	request_one.auth = (rpcuser,rpcpassword)
	response = request_one.request("POST", url, data=payload, headers=headers)
	if json.loads(response.text)["result"] != None:
		response = json.loads(response.text)["result"]	
		return response
	else:
		print(response.text)		
		return -1
def get_wallet_balance(Wallet):
	return RPC_call("getreceivedbyaddress",Wallet)

def save_user_lists():
	global main_json
	import json
	with open("Users.json", "w") as file:
		file.write(json.dumps(main_json))
def get_balances_json():
	global main_json
	with open("Users.json", "r") as file:
		temp = file.read()
		temp = json.loads(temp)
		main_json = temp
def find_user_balance(User_ID):
	global main_json
	return find_user_attribute(User_ID,"Balance")
		
def change_user_balance(user_id, value_to_change_by):		
	global main_json
	get_balances_json()
	if find_user_balance(user_id) == None: #returns an error
		return 1
	for x in range(0,len(main_json["Users"])):
		if main_json["Users"][x]["User_ID"] == user_id:
			user_number = x	
	try:
		main_json["Users"][user_number]["Balance"] = str( Fraction( main_json["Users"][user_number]["Balance"] ) + Fraction(value_to_change_by) )
		save_user_lists()
		return 0
	except Exception as t:
		print("AN ERROR OCCURED:")
		print(t)
		return 1
def check_incoming_transactions(Tx_ID):
	global main_json
	get_balances_json()
	try:
		Transaction = RPC_call("gettransaction",str(Tx_ID))["details"]
	except:
		print("error in checking transaction...\n writing to log")
		with open("error.log","a") as file:
			file.write("error running gettransaction: \n")
	for x in range(0,len(Transaction)):
		if Transaction[x]["category"] == "send":
			return 1
		elif Transaction[x]["category"] == "generate":
			amount = Transaction[x]["amount"]
			while change_user_balance("FAUCET-BALANCE",amount) != 0:
						print("Transfering Block Reward to Faucet")
		else:
			address = Transaction[x]["address"]
			amount = Transaction[x]["amount"]
			for x in range(0,len(main_json["Users"])):
				if main_json["Users"][x]["Wallet-Addr"] == address:
					while change_user_balance(main_json["Users"][x]["User_ID"],amount) != 0:
						print("attempting transfer of balance...")
					PM_User(main_json["Users"][x]["User_ID"],"Your Transaction of " + str(amount) + "GRC has been recieved")
def generate_new_address(User_ID):
	get_balances_json()
	New_Address = RPC_call("getnewaddress","")
	for x in range(0,len(main_json["Users"])):
		if main_json["Users"][x]["User_ID"] == User_ID:
			number = x
	main_json["Users"][number]["Wallet-Addr"] = New_Address
	save_user_lists()
	return New_Address
def withdraw(user_id,amount,walletaddr):
	Balance = find_user_attribute("Balance",user_id)
	output = RPC_call("sendtoaddress",[walletaddr,float(amount)-0.5]) 
	if output == -1:		
		return 1
	if change_user_balance(user_id,-0.5 * amount) != 0:
		pass
	if change_user_balance("FEE-COLLECTION",1):
		pass
	return output
