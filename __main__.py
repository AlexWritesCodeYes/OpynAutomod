import json
from thebot import client
import welcome, config

with open('config.json') as c:
	data = json.load(c)
	token = data["TOKEN"]

client.run(token)