import nextcord, datetime, sqlite3
from nextcord.ext import commands

from thebot import client, executeQuery, guild_ids

@client.slash_command(name="logchannel", description="sets the channel to which this bot logs events", guild_ids=guild_ids)
async def logchannel(interaction: nextcord.Interaction, channel: nextcord.abc.GuildChannel = None):
	channelName = channel.name
	channelID = channel.id;
	logMessage = "The log channel was set to " + channelName

	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()
		findQuery = "SELECT name FROM channels WHERE name='log'"
		result = cursor.execute(findQuery)

		nextQuery = ""
		if(result is None or result.fetchone() is None):
			nextQuery = "INSERT INTO channels(name, channelID) VALUES('log','{}')".format(channelID)
		else:
			nextQuery = "UPDATE channels SET channelID={} WHERE name='log'".format(channelID)
		cursor.execute(nextQuery)
		connection.commit()
		print("executed query: " + nextQuery)
		cursor.close()
	except sqlite3.Error as error:
		logMessage = "There was a sqlite3 error. Here it is: {}".format(error)
		print(logMessage)
	finally:
		if(connection):
			connection.close()
		await interaction.response.send_message(logMessage, ephemeral=False)