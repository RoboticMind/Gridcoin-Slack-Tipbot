import sys
import requests
try:
	message = str(sys.argv[1])
except:
	with open("error.log", "a") as file:
		file.write("\nerror invalid input to start_check")
		sys.exit()
with open("Config/verification_token.txt", "r") as file:
	verification_token = file.read().replace("\n","")
send = requests.Session()
send.request("POST","http://127.0.0.1:5000/new_transaction",data={"TX_ID":message,"Token":verification_token},headers={"TX_ID":message})