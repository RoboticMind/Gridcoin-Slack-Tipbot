from RPC import *
from Slack_Connection import *
from flask import Flask, request, Response
from decimal import *
from fractions import *
from Python_Hash import *
import os
import time

app = Flask(__name__)

def get_minimum_transaction_size():
	with open("Config/min-transaction-size.txt") as file:
		return Fraction(file.read())

def get_balances_json():
	global main_json
	import json
	with open("Users.json", "r") as file:
		temp = file.read()
		temp = json.loads(temp)
		main_json = temp

def find_user_attribute(user_id,type_of_input):
	global main_json
	get_balances_json()	
	for x in range(0,len(main_json["Users"])):
		if main_json["Users"][x]["User_ID"] == user_id:
			return_value = main_json["Users"][x][type_of_input]
	if "return_value" in locals():
		return return_value
	else:
		return None
def save_user_lists():
	global main_json
	import json
	with open("Users.json", "w") as file:
		file.write(json.dumps(main_json))
def set_user_attribute(user_id,type_of_input,value):
	global main_json
	get_balances_json()
	for x in range(0,len(main_json["Users"])):
		if main_json["Users"][x]["User_ID"] == user_id:
			main_json["Users"][x][type_of_input] = value
			save_user_lists()
			return_value=0
	if "return_value" in locals():
		return 0
	else:
		return 1
def add_user(User_ID, Balance):
	global main_json
	main_json["Users"].append({"User_ID":User_ID, "Balance":str(Balance), "Password":"","Salt":"","Wallet-Addr":"","Faucet_Time":""})
	save_user_lists()

def find_user_balance(User_ID):
	global main_json
	for x in range(0,len(main_json["Users"])):
		if main_json["Users"][x]["User_ID"] == User_ID:
			return_value = main_json["Users"][x]["Balance"]
	if "return_value" in locals():
		return return_value
	else:
		return None
		
def find_user_password(User_ID):
	global main_json
	for x in range(0,len(main_json["Users"])):
		if main_json["Users"][x]["User_ID"] == User_ID:
			return_value = main_json["Users"][x]["Password"]
	if "return_value" in locals():
		return return_value
	else:
		return None

def change_user_balance(user_id, value_to_change_by):
	global main_json
	if find_user_balance(user_id) == None: #adds the user to the json file if they arn't there already
		add_user(user_id,0)
	for x in range(0,len(main_json["Users"])):
		if main_json["Users"][x]["User_ID"] == user_id:
			user_number = x
	try:
		main_json["Users"][user_number]["Balance"] = str(Fraction(main_json["Users"][user_number]["Balance"]) + Fraction(value_to_change_by))
		save_user_lists()
		return 0
	except Exception as t:
		print("AN ERROR OCCURED:\n"+str(t))
		return 1

def transfer_money(User_ID_to_take_from, User_ID_to_give_to, value,channel_id):
	if change_user_balance(User_ID_to_take_from, -1*value) == 1:
		send_message_to_one_user("An Error Occurred While Transferring Please Contact Roboticmind",channel_id,User_ID_to_take_from)
		return 1
	elif change_user_balance(User_ID_to_give_to,value) == 1:
		change_user_balance(User_ID_to_take_from, value)
		send_message_to_one_user("An Error Occurred While Transferring. Please Contact Roboticmind",channel_id,User_ID_to_take_from)
		return 1
	else:
		return 0

def Check_Valid_Addr(Address):
	if len(Address) != 34:
		return True
	elif Address[0] != "S" and Address[0] != "R":
		return False
	for x in range(1,35):
		if Address[x] in ["0","O","I","L"]:
			return False
	return True

def run_command(command, text, user_id, channel_id, code, trigger_id):	
	global main_json
	get_balances_json()
	if command == "/tip": #tip user amount password
		try:
			text = text.split(",")
		except:
			send_message_to_one_user("*Error:* Please Enter a Valid Command",channel_id,user_id)
			return
		if find_user_balance(user_id) == None:
			send_message_to_one_user("*Error:* This account is not registered use /register",channel_id,user_id)
			return
		elif len(text) <= 1:
			if code == "":
				code="Info_Sent"
				command_info=json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":code})
				selection=[{
					"label":"Who Do You Want To Tip?",
					"name":"user","text":"select a user",
					"type":"select",
					"data_source":"users"
				},
				{
					"label":"How Many Gridcoin?",
					"name":"amount",
					"text":"type an amount",
					"type":"text",
					"subtext":"number"
				}	
				]
				if find_user_password(user_id) != "":
					selection.append({
					"label":"Your Password",
					"name":"password",
					"text":"type an amount",
					"type":"text",
					"subtext":"number"
					})
				GUI("Tip A User Gridcoin!",selection,command_info,trigger_id)
				return
			else:
				info=json.loads(code.split("|")[1])
				if info.get("password") != None:
					password = "," + info["password"]
				else:
					password = ""
				run_command("/tip", info["user"] + "," + info["amount"] + password,user_id,channel_id,"",None)
				return
		elif text[0][0] == "@": #this looks at the starting char in the input
			send_message_to_one_user("*Error:* Please Don't Use Tagged Usernames (I.E: @User)",channel_id,user_id)		
			return
		
		password=find_user_password(user_id)
		if password != "":
			if len(text) < 3:
				send_message_to_one_user("*Error:* Please Enter a Command with a user to tip, an amount to tip, and this account requires a password",channel_id,user_id)
				return
			amount=text[len(text)-2]
			users=text[0:len(text)-2]
			user_ids = get_multiple_user_ids(text[0:len(text)-2])
			inputted_password=text[len(text)-1]
			salt=find_user_attribute(user_id,"Salt")
			if not checkpassword(inputted_password,password,salt):
				send_message_to_one_user("*Error:* Incorrect Password",channel_id,user_id)
				return
		else:
			amount=text[len(text)-1]
			user_ids = get_multiple_user_ids(text[0:len(text)-1])
			users=text[0:len(text)-1]
		users_list_text=""
		try:
			Fraction(amount)
		except:
			send_message_to_one_user("*Error:* Please Enter a Valid Command with a number for the amount",channel_id,user_id)
			return
		
		if Fraction(find_user_balance(user_id)) < Fraction(amount):
			send_message_to_one_user("*Error:* Account Balance Is Lower Than the Amount Attempted to be Transferred",channel_id,user_id)
			return
		
		elif Decimal(amount).as_tuple().exponent < -8:
				send_message_to_one_user("*Error:* Only 8 Decimal Places Are Supported",channel_id,user_id)
				return
			
		elif Fraction(amount) < get_minimum_transaction_size():
			send_message_to_one_user("*Error:* Transaction size is under the minimum transaction size of " + str(float(get_minimum_transaction_size())) + " GRC",channel_id,user_id)
			return
				
		elif user_id in user_ids:
			send_message_to_one_user("*Error:* You Can Not Send Gridcoin To Yourself",channel_id,user_id)
			return
			
		elif len(user_ids) < len(users):
			send_message_to_one_user("*Error:* One Of The Usernames Inputted Is Invalid",channel_id,user_id)
			return
		elif Fraction(amount) >= 25 and code != "CONFIRMED|Yes":
			Confirm("Are you sure you want to tip " + amount + "GRC?",channel_id,user_id,json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":"CONFIRMED"}))
			return
		for x in range(0,len(user_ids)):
			if transfer_money(user_id,user_ids[x],Fraction(amount)/len(user_ids),channel_id) == 1:
				send_message_to_one_user("*Error Transferring Gridcoin*",channel_id,user_id)
				for l in range(0,x):
					transfer_money(user_id,user_ids[l],Fraction(amount)/len(user_ids),channel_id)
				return
		
		for x in range(0,len(user_ids)):
			users_list_text+= " |<@" + user_ids[x] + ">|"			

		if can_bot_post(channel_id):
			send_message_by_id(channel_id,"<@" + user_id + ">" + " tipped " + str(round(float(Fraction(amount)/Fraction(len(user_ids))),8)) + " GRC to" + users_list_text)
			return
		else:
			PM_User(user_id,"<@" + user_id + ">" + " tipped " + str(round(float((Fraction(amount)/Fraction(len(user_ids))),8))) + " GRC to" + users_list_text)
			for x in range(0,len(user_ids)):
				PM_User(user_ids[x],"<@" + user_id + ">" + " tipped " + text[amount] + " GRC to" + users_list_text)
			return
	elif command == "/withdraw": #withdraw address amount password	
		try:
			text = text.split(",")
		except:
			send_message_to_one_user("*Error:* Please Enter a Valid Command",channel_id,user_id)
			return
		if len(text) < 2 or len(text) > 3:
			if code == "":
				code="Info_Sent"
				command_info=json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":code})
				selection=[{
					"label":"Your Gridcoin address",
					"name":"address",
					"text":"enter an address",
					"type":"text",
				},
				{
					"label":"How Many Gridcoin?",
					"name":"amount",
					"text":"type an amount",
					"type":"text",
					"subtext":"number"
				}	
				]
				if find_user_password(user_id) != "":
					selection.append({
					"label":"Your Password",
					"name":"password",
					"text":"type an amount",
					"type":"text",
					"subtext":"number"
					})
				GUI("Withdrawl Your Gridcoin",selection,command_info,trigger_id)
				return
			else:
				info=json.loads(code.split("|")[1])
				if info.get("password") != None:
					password = "," + info["password"]
				else:
					password = ""
				run_command("/withdraw", info["address"] + "," + info["amount"] + password,user_id,channel_id,"",None)
				return
			send_message_to_one_user("*Error:* Invalid Command",channel_id,user_id)
			return
		try:
			Fraction(text[1])
		except:
			send_message_to_one_user("*Error:* Invalid Input",channel_id,user_id)
			return
		if find_user_attribute(user_id,"User_ID") == None:
			send_message_to_one_user("*Error:* Your Account Is Not Registered Yet\n Use /register to register your account",channel_id,user_id)
		elif Fraction(text[1]) < get_minimum_transaction_size() or Fraction(text[1]) < 0.6:
			send_message_to_one_user("*Error:* Transaction too small",channel_id,user_id)
			retur
		elif Fraction(text[1]) > Fraction(find_user_attribute(user_id,"Balance")):
			send_message_to_one_user("*Error:* Your Balance Is Less Than The Amount You Are Trying To Transfer",channel_id,user_id)
			return
		elif not Check_Valid_Addr(text[0]):
			send_message_to_one_user("*Error* Invalid Address",channel_id,user_id)
		elif find_user_password(user_id) != "":
			if len(text) != 3:
				send_message_to_one_user("*Error:* Please Enter a password\n This account requires a password",channel_id,user_id)
				return
			else:
				password = find_user_password(user_id)
				salt = find_user_attribute(user_id,"Salt")
				if not checkpassword(text[2],password,salt):
					send_message_to_one_user("*Error:* incorrect password",channel_id,user_id)
					return
		output = withdraw(user_id,Fraction(text[1]),text[0])
		if output != 1:
			send_message_to_one_user("successful withdrawal of " + text[1]+ " Gridcoin (With a Fee of 0.5 GRC)\nTransaction ID:" + str(output),channel_id,user_id)
		else:
			send_message_to_one_user("An Error Occurred",channel_id,user_id)
	elif command == "/deposit":
		for x in range(0,len(main_json["Users"])):
			if main_json["Users"][x]["User_ID"] == user_id:
				number = x
		try:
			if main_json["Users"][number]["Wallet-Addr"] != "":
				Address=main_json["Users"][number]["Wallet-Addr"]
			else:
				Address=generate_new_address(user_id)
			send_message_to_one_user("Deposit Your Gridcoins To This Address:\n*`"+Address+"`*\nOnce You Send a Transaction To That Address, Don't Send Any More To It Until You Receive Confirmation That Your Transaction Was Received",channel_id,user_id)
		except:
			send_message_to_one_user("*Error:* Your account isn't registered yet, use /register",channel_id,user_id)
	elif command == "/password": # /password add [password] or /password change Old_Password New_password or /password remove [password] or /password help
		try:
			text = text.split(",")
		except:
			send_message_to_one_user("*Error:* Please Enter a Valid Command",channel_id,user_id)
			return
		if text[0] == "help":
			send_message_to_one_user("The /password command can add, change, or remove an extra layer of protection\nTo add a password use:\n/password add,[Password]\nTo change your password use:\n/password change,[Old_Password],[New_Password]\nTo Remove Your Password Use:\n/password remove,[Password]\nDon't use spaces in your password\nIf you have forgotten your password please contact Roboticmind ",channel_id,user_id)
			return
		elif text[0] == "add":
			password = find_user_password(user_id)
			salt = find_user_attribute("Salt",user_id)
			if password != None and password != "":
				send_message_to_one_user("*Error:* there already is a password on this account",channel_id,user_id)
			if len(text) == 1:
				if code == "":
					code="Info_Sent"
					command_info=json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":code})
					selection=[{
						"label":"Your New Password",
						"name":"password",
						"text":"enter a password",
						"type":"text",
					}]
					GUI("Set a Password",selection,command_info,trigger_id)
				else:
					info=json.loads(code.split("|")[1])
					run_command("/password", "add," + info["password"],user_id,channel_id,"",None)
					return
			elif len(text) > 2:
				send_message_to_one_user("*Error:* Please Don't Use Commas In Your Password",channel_id,user_id)
				return
			elif password == "":
				for x in range(0,len(main_json["Users"])):
					if main_json["Users"][x]["User_ID"] == user_id:
						password, salt = newpassword(text[1])
						main_json["Users"][x]["Password"] = password
						main_json["Users"][x]["Salt"] = salt
						save_user_lists()
						send_message_to_one_user("Your Password Has Been Added",channel_id,user_id)
				return
			elif password == None:
				add_user(user_id,0)
				for x in range(0,len(main_json["Users"])):
					if main_json["Users"][x]["User_ID"] == user_id:
						new_password, new_salt = newpassword(text[1])
						main_json["Users"][x]["Password"] = new_password
						main_json["Users"][x]["Salt"] = new_salt
						save_user_lists()
				send_message_to_one_user("Your Account Has Been Created And Your Password Has Been Added",channel_id,user_id)
				return
		elif text[0] == "change":
			password = find_user_password(user_id)
			salt = find_user_attribute(user_id,"Salt")
			if len(text) <= 2:
				if code == "":
					code="Info_Sent"
					command_info=json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":code})
					selection=[
					{
						"label":"Your Old Password",
						"name":"old-password",
						"text":"enter your current password",
						"type":"text"
					},
					{
						"label":"Your New Password",
						"name":"new-password",
						"text":"enter a new password",
						"type":"text",
					}]
					GUI("Change Your Password",selection,command_info,trigger_id)
				else:
					info=json.loads(code.split("|")[1])
					run_command("/password", "change," + info["old-password"] + ","+info["new-password"],user_id,channel_id,"",None)
					return
			elif len(text) > 3:
				send_message_to_one_user("*Error:* Please Don't Use Commas In Your Password",channel_id,user_id)
				return
			elif password == None or password == "":
				send_message_to_one_user("*Error:* There is no password set",channel_id,user_id)
				return
			elif checkpassword(text[1],password,salt):
				for x in range(0,len(main_json["Users"])):
					if main_json["Users"][x]["User_ID"] == user_id:
						new_password, new_salt = newpassword(text[2])
						main_json["Users"][x]["Password"] = new_password
						main_json["Users"][x]["Salt"] = new_salt
						save_user_lists()
						send_message_to_one_user("Your Password Has Been Changed",channel_id,user_id)
				return
			else:
				send_message_to_one_user("*Error:* Incorrect Password\n Contact Roboticmind if you have forgotten your password",channel_id,user_id)
				return
		elif text[0] == "remove":
			password = find_user_password(user_id)
			salt = find_user_attribute(user_id,"Salt")
			if password == None or password == "":
				send_message_to_one_user("*Error:* No Password Registered On This Account",channel_id,user_id)
				return
			elif len(text) != 2:
				if code == "":
					code="Info_Sent"
					command_info=json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":code})
					selection=[
					{
						"label":"Your Current Password",
						"name":"current-password",
						"text":"enter your current password",
						"type":"text"
					}]
					GUI("Remove a Password",selection,command_info,trigger_id)
				else:
					info=json.loads(code.split("|")[1])
					run_command("/password", "remove," + info["current-password"],user_id,channel_id,"",None)
					return
			elif not checkpassword(text[1],password,salt):
				send_message_to_one_user("*Error* Incorrect Password",channel_id,user_id)
				return
			else:
				for x in range(0,len(main_json["Users"])):
					if main_json["Users"][x]["User_ID"] == user_id:
						main_json["Users"][x]["Password"] = ""
						main_json["Users"][x]["Salt"] = ""
						save_user_lists()
						send_message_to_one_user("Your Password Has Been Removed",channel_id,user_id)
						return
		elif text[0] == "":
			if code == "":
				code="Info_Sent"
				command_info=json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":code})
				selection=[{
					"name":"option",
					"text":"Select a Password Change",
					"type":"select",
					"options":[
						{
							"text":"Add A Password",
							"value":"add"
						},
						{
							"text":"Change A Password",
							"value":"change"
						},
						{
							"text":"Remove A Password",
							"value":"remove"
						},
					]}]
				GUI_no_popup("Password Settings",selection,channel_id,user_id,command_info)
				return
			else:
				info=json.loads(code.split("|")[1])
				run_command("/password", info,user_id,channel_id,"",trigger_id)
				return
			send_message_to_one_user("The /password command can add, change, or remove an extra layer of protection\nTo add a password use:\n/password add,[Password]\nTo change your password use:\n/password change,[Old_Password],[New_Password]\nTo Remove Your Password Use:\n/password remove,[Password]\nDon't use Commas in your password\nIf you have forgotten your password please contact Roboticmind ",channel_id,user_id)
		else:
			send_message_to_one_user("*Error:* Invalid Command",channel_id,user_id)
			return
	elif command == "/balance": #/balance or /balance password
		return_value = find_user_attribute(user_id,"Balance")
		if return_value == None:
			send_message_to_one_user("*Error:* this account is not registered yet\n Use /register to register your account",channel_id,user_id)
			return
		else:
			send_message_to_one_user("Your Balance Is:\n" + str(round(float(Fraction(return_value)),8)) + " GRC",channel_id,user_id)
	elif command == "/register": #/register or /register password
		for x in range(0,len(main_json["Users"])):
			if main_json["Users"][x]["User_ID"] == user_id:
				number = x
		if "number" in locals():
			send_message_to_one_user("*Error:* Your account is already registered, someone may have sent you Gridcoin already",channel_id,user_id)
			return
		else:
			if text == "":
				add_user(user_id,0)
				send_message_to_one_user("Your account has been registered!",channel_id,user_id)
			elif len(text) >= 1:
				add_user(user_id,0)
				for x in range(0,len(main_json["Users"])):
					if main_json["Users"][x]["User_ID"] == user_id:
						new_password, new_salt = newpassword(text)
						main_json["Users"][x]["Password"] = new_password
						main_json["Users"][x]["Salt"] = new_salt
						save_user_lists()
				send_message_to_one_user("Your account has been registered!",channel_id,user_id)
			else:
				send_message_to_one_user("*Error:* Invalid Command. Commas Are Not Allowed In Passwords",channel_id,user_id)
	elif command == "/test":
		send_message_to_one_user("the bot is working",channel_id,user_id)
	elif command == "/attribution":
		send_message_to_one_user("The bot icon picure can be found at https://www.shareicon.net/gridcoin-grc-117383",channel_id,user_id)
	elif command == "/faucet": #faucet give amount password or faucet receive
		try:
			text = text.split(",")
		except:
			send_message_to_one_user("*Error:* Invalid Input",channel_id,user_id)
			return
		if len(text) > 3 or text[0] == "":
			if code == "":
				code="Info_Sent"
				command_info=json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":code})
				selection=[{
					"name":"option",
					"text":"Select a Password Change",
					"type":"select",
					"options":[
						{
							"text":"Recieve Gridcoin from the faucet",
							"value":"receive"
						},
						{
							"text":"Donate to the faucet",
							"value":"give"
						}
					]}]
				GUI_no_popup("Fuacet Options",selection,channel_id,user_id,command_info)
				return
			else:
				info=json.loads(code.split("|")[1])
				run_command("/faucet", info,user_id,channel_id,"",trigger_id)
				return
		if text[0] == "give":
			if len(text) == 1:
				if code == "":
					code="Info_Sent"
					command_info=json.dumps({"0":command,"1":",".join(text),"2":user_id,"3":channel_id,"4":code})
					selection=[{
						"label":"Amount To Be Donated",
						"name":"amount",
						"text":"type an amount",
						"type":"text",
						"subtext":"number"
					}]
					if find_user_password(user_id) != "":
						selection.append({
						"label":"Your Password",
						"name":"password",
						"text":"type your password",
						"type":"text",
						"subtext":"number"
						})
					GUI("Donate To The Faucet!",selection,command_info,trigger_id)
					return
				else:
					info=json.loads(code.split("|")[1])
					if info.get("password") != None:
						password = "," + info["password"]
					else:
						password = ""
					run_command("/faucet give," + info["amount"] + password,user_id,channel_id,"",None)
					return
			try:
				Fraction(text[1])
			except:
				send_message_to_one_user("*Error:* Please Enter a Valid Number")
				return
			password=find_user_password(user_id)
			salt=find_user_attribute(user_id,"Salt")
			if password == None:
				send_message_to_one_user("*Error:* Your Account Is Not Registered Yet, Use /register",channel_id,user_id)
				return
			elif Fraction(find_user_balance(user_id)) < Fraction(text[1]):
					send_message_to_one_user("*Error:* Account Balance Is Lower Than the Amount Attempted to be Transferred",channel_id,user_id)
					return
			elif Decimal(text[1]).as_tuple().exponent < -8:
				send_message_to_one_user("*Error:* Only Eight Decimal Places Are Supported")
				return
			elif Fraction(text[1]) < get_minimum_transaction_size():
				send_message_to_one_user("*Error:* Transaction Too Small*",channel_id,user_id)
				return
			if password != "":
				if len(text) != 3:
					send_message_to_one_user("*Error:* Invalid Input, Please Make Sure You Have a Password and Have Two Commas",channel_id,user_id)
					return
				elif not checkpassword(text[2],password,salt):
					send_message_to_one_user("*Error* Incorrect Password",channel_id,user_id)
					return
			if transfer_money(user_id,"FAUCET-BALANCE",Fraction(text[1]),channel_id) == 0:
				if can_bot_post(channel_id):						
					send_message_by_id(channel_id,"<@" + user_id + ">" + " tipped " + text[1].replace(" ","") + " GRC to the Faucet")
					return
				else:
					PM_User(user_id,"Your Deposit Was Sucessful")
					return
		elif text[0] == "receive":
			if Fraction(find_user_attribute("FAUCET-BALANCE","Balance")) <= Fraction(0):
				send_message_to_one_user("*Error:* The Faucet Is Currently Empty",channel_id,user_id)
				return
			elif find_user_attribute(user_id,"Faucet_Time") != None and find_user_attribute(user_id,"Faucet_Time") != "" and int(time.time()) - int(find_user_attribute(user_id,"Faucet_Time")) < 86400:
				send_message_to_one_user("*Error:* Please Wait " + time.strftime("%H hours, %M minutes, and %S seconds",time.gmtime(int(find_user_attribute(user_id,"Faucet_Time"))-int(time.time()+86400))),channel_id,user_id)
				return
			elif Fraction(find_user_attribute("FAUCET-BALANCE","Balance")) < Fraction(0.5):
				amount=Fraction(find_user_attribute("FAUCET-BALANCE","Balance"))
			else:
				amount=Fraction(0.5)
			transfer_money("FAUCET-BALANCE",user_id,amount,channel_id)
			if set_user_attribute(user_id,"Faucet_Time",int(time.time())) == 1:
				transfer_money("FAUCET-BALANCE",user_id,-amount,channel_id)
				send_message_to_one_user("An Error Occured",channel_id,user_id)
			send_message_to_one_user("You have sucessfully received" + str(round(float(amount),8)) +" GRC",channel_id,user_id)
		else:
			run_command("/faucet", "",user_id,channel_id,"",trigger_id)
			return
	elif command == "/helpgrctip":
		if text == "":
			text="1"
		try:
			with open("Config/Help_Messages/" + text + ".txt","r") as file:
				send_message_to_one_user(file.read(),channel_id,user_id)
		except:
			send_message_to_one_user("*Error:* No Help Menu Exists For That Number",channel_id,user_id)
	elif command == "/tos":
		send_message_to_one_user("By using this bot you are agreeing to these terms of service listed as follows: You are agreeing to not use this bot to scam, launder money or do anything illegal. This bot may temporarily go offline at any point where you might not be able to withdraw Gridcoin until it is back online. Any violation of the terms of service may result in account cancelltion and or reported to the proper authorities.",channel_id,user_id)

@app.route("/" ,methods=["POST"])
def inbound():
	run_command(request.form.get("command"),request.form.get("text"),request.form.get("user_id"),request.form.get("channel_id"),"",request.form.get("trigger_id"))
	return Response(), 200

@app.route("/Button_Pressed",methods=["POST"])
def reaction():
	response = json.loads(request.form.get("payload"))
	
	if response["token"] != get_verification_token():
		return Response(),400
	
	if response["type"] == "interactive_message":
		if response["actions"][0].get("value") == "No":
			return Response("*Request Cancelled*"), 200
		else:
			print(response["actions"][0])
			try:
				value=response["actions"][0]["selected_options"][0]["value"]
			except:
				value=response["actions"][0].get("value") 
			inputs=json.loads(response["callback_id"])
			run_command(inputs["0"],inputs["1"],inputs["2"],inputs["3"],inputs["4"] + "|" + json.dumps(value),response["trigger_id"])
			return Response("*Input Confirmed*"), 200
	value=response["submission"]
	inputs=json.loads(response["callback_id"])
	run_command(inputs["0"],inputs["1"],inputs["2"],inputs["3"],inputs["4"] + "|" + json.dumps(value),None)
	return Response(""), 200
@app.route("/", methods=['GET'])
def test():
	return Response(),200

@app.route("/new_transaction",methods=["POST"])
def check():
	if get_verification_token() != request.form.get("Token"):
		print("ALERT: NEW TRANSACTION WITH INCORRECT TOKEN")
		return Response(),400
	check_incoming_transactions(request.form.get("TX_ID"))
	return Response(),200
if __name__ == "__main__":	
	global main_json
	app.run(debug=False,threaded=True)
