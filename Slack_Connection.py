from slackclient import SlackClient
import requests

def get_token():
	global token	
	if "token" == globals():
		return token
	else:
		with open("Config/token.txt", "r") as file:
			token = file.read()
		return token
def get_verification_token():
	global verification_token	
	if "verification_token" == globals():
		return verification_token
	else:
		with open("Config/verification_token.txt", "r") as file:
			verification_token = file.read().replace("\n","")
		return verification_token
def SlackConnection():
	global slack_client
	if "slack_client" in globals():
		pass
	else:
		slack_client = SlackClient(get_token())
def can_bot_post(channel_id):
	global slack_client
	SlackConnection()
	a = slack_client.api_call("groups.info",channel=channel_id)
	b = slack_client.api_call("channels.info",channel=channel_id)
	if a["ok"] or b["ok"]:
		return True
	else:
		return False

def send_message_by_id(channel_id, message):
	global slack_client
	SlackConnection()
	slack_client.api_call("chat.postMessage",channel=channel_id,text=message,username="GRCTip",icon_url="https://www.shareicon.net/download/512x512/2016/07/08/117383_grc_512x512.png")

def get_user_id(username):
	global slack_client
	SlackConnection()
	cursor=""
	while True:
		data = slack_client.api_call("users.list",cursor=cursor,limit=200)
		members = data["members"]
		cursor = data["response_metadata"]["next_cursor"]
		for x in range(0, len(members)):
			if members[x]["profile"].get("display_name_normalized") == username or members[x].get("real_name") == username or members[x]["id"] == username:
					return_value = members[x]["id"]
		if "return_value" in locals():
			return return_value
		else:
			if cursor == "":
				return None
def get_multiple_user_ids(usernames):
	global slack_client
	SlackConnection()
	cursor=""
	while True:
		data = slack_client.api_call("users.list",cursor=cursor,limit=200)
		members = data["members"]
		member_ids=[]
		cursor = data["response_metadata"]["next_cursor"]
		for x in range(0, len(members)):
			if members[x].get("real_name") in usernames or members[x]["profile"].get("display_name_normalized") in usernames or members[x]["id"] in usernames:
					member_ids.append(members[x]["id"])
		return member_ids	
def PM_User(user_id, message):
	global slack_client
	SlackConnection()
	try:
		PM_Channel = slack_client.api_call("im.open",user=user_id)["channel"]["id"]
	except:
		return 1
	send_message_by_id(PM_Channel,message)

def send_message_to_one_user(message, channel_id, user_id):
	global slack_client
	SlackConnection()
	result = slack_client.api_call("chat.postEphemeral",channel=channel_id,user=user_id,text=message)
	if not result["ok"]:
		PM_User(user_id,message)
def Confirm(message,channel_id,user_id,data):
	global slack_client
	SlackConnection()
	attachments=[{
	"text":message,
	"fallback":message,
	"callback_id":str(data),
	"color":"warning",
	"actions":[
		{
			"name":"Yes",
			"text":"Yes",
			"type":"button",
			"value":"Yes",
			"style":"primary"
		},
		{
			"name":"No",
			"text":"No",
			"type":"button",
			"value":"No",
			"style":"danger"
		}
	]
	}]
	response = slack_client.api_call("chat.postEphemeral",channel=channel_id,user=user_id,attachments=attachments)
	if not response["ok"]:
		print(response)
def GUI_no_popup(message,actions,channel_id,user_id,data):
	global slack_client
	SlackConnection()
	attachments=[{
	"text":message,
	"fallback":message,
	"callback_id":str(data),
	"color":"warning",
	"actions":actions
	}]
	response = slack_client.api_call("chat.postEphemeral",channel=channel_id,user=user_id,attachments=attachments)
	if not response["ok"]:
		print(response)
def GUI(message,elements,data,trigger_id):
	global slack_client
	SlackConnection()
	dialog={
	"title":message,
	"fallback":message,
	"callback_id":str(data),
	"color":"warning",
	"elements":elements
	}
	response = slack_client.api_call("dialog.open",dialog=dialog,trigger_id=trigger_id)
	if not response["ok"]:
		print(response)