import nextcord, sqlite3
from nextcord.ext import commands
from nextcord import SlashOption
from typing import Optional

from thebot import client, guild_ids, minute, hour, day

@client.slash_command(name="channels", description="adds to, removes from, or lists the contents of the automod channel exclusion list", guild_ids=guild_ids)
async def channels(interaction: nextcord.Interaction):
	pass

@channels.subcommand(description="Adds a channel to the ignore list for one or many automod features")
async def ignore(
	interaction: nextcord.Interaction, 
	channel: nextcord.abc.GuildChannel = SlashOption(
		description="The channel for the automod feature(s) to ignore", 
		required=True
		),
	phrases: bool = SlashOption(
		description="Ignore this channel for the phrase-response system?",
		choices={"Yes": True, "No": False},
		required=True
		),
	mention: bool = SlashOption(
		description="Ignore this channel for the mention spam protection feature?",
		choices={"Yes": True, "No": False},
		required=True
		),
	spam: bool = SlashOption(
		description="Ignore this channel for the suspected spam protection feature?",
		choices={"Yes": True, "No": False},
		required=True
		),
):
	message = ""
	if((phrases is False) and (mention is False) and (spam is False)):
		message = "Please specify at least one feature to ignore for the channel."
		await interaction.response.send_message(message, ephemeral=True)
	else:
		insertionQuery = "INSERT INTO blacklist(channelID,category) VALUES ('"
		category = ""
		channelID = str(channel.id)
		if(phrases):
			category = category + "phrases "
		if(mention):
			category = category + "mention "
		if(spam):
			category = category + "spam "
		category = category.rstrip()

		insertionQuery = insertionQuery + channelID + "','" + category + "')"
		print(insertionQuery)
		
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()
		try:
			cursor.execute(insertionQuery)
			connection.commit()

			message = message + "Successfully added " + channel.name + " to the following ignore lists: `" + category + "`"
		except sqlite3.Error as error:
			if("UNIQUE" in str(error).split(' ')):
				try:
					message = str(channel.name) + " was already being excluded from one or more features. Attempting to update with the new selections... "
					updateQuery = "UPDATE blacklist SET category='" + category + "' WHERE channelID='" + channelID + "'"

					cursor.execute(updateQuery)
					connection.commit()
				except sqlite3.Error as error:
					message = message + "Failed. There was a sqlite3 error. Here it is: {}".format(error)
				finally:
					message = message + "Success! " + channel.name + " is now being excluded from the following automod categories: `" + category + "`"
					print(message)
			else:
				message = message + "There was a sqlite3 error. Here it is: {}".format(error)
				print(message)
		finally:
			cursor.close()
			if(connection):
				connection.close()
			await interaction.response.send_message(message, ephemeral=False)

@channels.subcommand(description="Removes a channel from the ignore list(s)")
async def unignore(
	interaction: nextcord.Interaction, 
	channel: nextcord.abc.GuildChannel = SlashOption(
		description="The channel for the automod feature(s) to stop ignoring", 
		required=True
		),
):
	message = ""
	connection = sqlite3.connect("everything.db")
	cursor = connection.cursor()
	try:
		findQuery = "select * from blacklist"
		result = cursor.execute(findQuery)
		if(result is None):
			message = "Nothing was found in the database. Has it been /setup?"
		else:
			channelID = str(channel.id)
			deletionQuery = "DELETE FROM blacklist WHERE channelID='" + channelID + "'"
			findQuery = "SELECT category FROM blacklist WHERE channelID='" + channelID + "'"

			result = cursor.execute(findQuery)
			res = result.fetchone()

			if(result is None or res is None):
				message = "That channel was not found in any ignore list"
			else:
				cursor.execute(deletionQuery)
				connection.commit()

				message = "The automod features will no longer ignore " + channel.name
	except sqlite3.Error as error:
		message = message + "There was a sqlite3 error. Here it is: {}".format(error)
	finally:
		cursor.close()
		if(connection):
			connection.close()
		await interaction.response.send_message(message, ephemeral=False)

@channels.subcommand(description="Lists the contents of the channel ignore list")
async def list(interaction: nextcord.Interaction):
	message = ""
	connection = sqlite3.connect("everything.db")
	cursor = connection.cursor()
	try:
		findQuery = "select rowid,* from blacklist"
		results = cursor.execute(findQuery)
		results = results.fetchall()

		message = "-----channel blacklist-----\n"
		for result in results:
			rowid = str(result[0])
			channelID = result[1]
			category = result[2]

			channel = interaction.guild.get_channel(int(channelID))

			message = message + str(rowid) + ": channel: " + channel.name + " | categories: `" + category + "`\n"
			message = message + "------------------------\n"
	except sqlite3.Error as error:
		message = message + "There was a sqlite3 error. Here it is: {}".format(error)
	finally:
		cursor.close()
		if(connection):
			connection.close()
		await interaction.response.send_message(message, ephemeral=False)