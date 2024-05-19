import nextcord, datetime, sqlite3
from nextcord.ext import commands

from thebot import client, executeQuery, guild_ids

def formatDate(dateTime):
	dateString = dateTime.strftime('%Y-%m-%d %H:%M:%S')
	return dateString

async def grabMany(channel, options, msgList):
	lastID = options[1]
	tooMany = 100
	breakCondition = False
	while(True):
		if(lastID is not None):
			lastMsg = await channel.fetch_message(lastID)
			print(lastMsg.content)
			options = [tooMany, lastID]

			messages = await channel.history(limit=options[0],before=lastMsg).flatten()
			
			print('grabbed {} messages before {}'.format(len(messages), lastID))
			print(messages[0].content)
		else:
			print("lastID is " + ' : ', type(lastID))

		channelMessages = []
		if(lastID is not None):
			lastMsg = await channel.fetch_message(lastID)
			channelMessages = await channel.history(limit=options[0],before=lastMsg).flatten()
		else:
			channelMessages = await channel.history(limit=options[0]).flatten()

		myMessageList = []
		if(len(channelMessages) == tooMany):
			lastID = channelMessages[len(channelMessages) - 1].id
			options = [tooMany, lastID]
		else:
			print('only {} to go!'.format(len(channelMessages)));
			breakCondition = True;

		for message in channelMessages:
			messageString = formatDate(message.created_at) + " " + message.author.name + " " + message.content
			if(len(message.attachments) != 0):
				for attachment in message.attachments:
					messageString = messageString + " [file: " + attachment.url + " ]"
			messageString = messageString + "\n----------\n"
			myMessageList.append(messageString)

		print("grabbed {} messages this time".format(len(myMessageList)))
		if(breakCondition):
			return myMessageList
		else:
			newMessages = await grabMany(channel, options, myMessageList)

			for message in newMessages:
				myMessageList.append(message)

			print("total length: {}".format(len(myMessageList)))
			if(len(newMessages) < tooMany):
				print('returning {} messages'.format(len(myMessageList)))
				return myMessageList

@client.slash_command(name="archive", description="Archives the contents of a given welcome channel", guild_ids=guild_ids)
async def archive(interaction: nextcord.Interaction, channel: nextcord.abc.GuildChannel = None):
	channelName = channel.name
	tooMany = 100
	
	if(channelName[:7] != 'welcome'):
		await interaction.response.send_message("That's not a welcome channel! Please do not do that.", ephemeral=False)
	
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()
		findQuery = "SELECT channelID FROM channels WHERE name='log'"
		result = cursor.execute(findQuery)
		logChannelID = result.fetchone()
		
		if(result is None or logChannelID is None):
			await interaction.response.send_message("The log channel has not been set. Please set it with /logchannel before running this command", ephemeral=False)

		logChannel = client.get_channel(int(logChannelID[0]))

		msgList = []
		options = [tooMany, None]
		msgList = await grabMany(channel, options, msgList)

		logMessage = "{} messages in ".format(len(msgList)) + channelName + "\n"
		msgList.reverse()

		for msg in msgList:
			potentialMsg = logMessage + msg
			length = len(potentialMsg)
			if(length >= 2000):
				await logChannel.send(logMessage)
				logMessage = ""
			logMessage = logMessage + msg

		await logChannel.send(logMessage)

		if(len(msgList) > tooMany):
			await logChannel.send("{} is a lot of messages! In the future, please try to keep conversation in the welcome channels to fewer than {} messages".format(len(msgList), tooMany))

		await interaction.response.send_message("Success! The messages in " + channelName + " were archived.")
		
		cursor.close()
	except sqlite3.Error as error:
		logMessage = "There was a sqlite3 error. Here it is: {}".format(error)
		print(logMessage)
	finally:
		if(connection):
			connection.close()
