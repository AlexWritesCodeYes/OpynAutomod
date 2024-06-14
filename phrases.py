import nextcord, sqlite3
from nextcord.ext import commands
from nextcord import SlashOption
from typing import Optional

from thebot import client, guild_ids, minute, hour, day

@client.slash_command(name="phrases", description="adds, deletes, or modifies a phrase-response pair", guild_ids=guild_ids)
async def phrases(interaction: nextcord.Interaction):
	pass

@phrases.subcommand(description="Adds a phrase-response pair to the database")
async def add(
	interaction: nextcord.Interaction, 
	phrase: str = SlashOption(description="The phrase to give an autoresponse to", required=True), 
	response: str = SlashOption(description="The response text to the person who posted the phrase", required=True), 
	delete: bool = SlashOption(
		description="Delete the message containing the phrase?",
		choices={"Yes": True, "No": False},
		required=True
		),
	timeout: int = SlashOption(
		description="Time the user who posted the phrase out?",
		choices={"No": 0, "Yes, for a minute": minute, "Yes, for an hour": hour, "Yes, for a day": day},
		required=True
		),
):
	deletionVal = 0
	if(delete): deletionVal = 1
	message = ""
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()
		
		insertionQuery = "INSERT INTO phrases(phrase, response, deletion, timeout) VALUES("
		insertionQuery = insertionQuery + "'" + phrase + "','" + response + "','" + str(deletionVal) + "','" + str(timeout) + "')"

		cursor.execute(insertionQuery)
		connection.commit()
		cursor.close()

		message = message + "Successfully added ||" + phrase + "|| "
	except sqlite3.Error as error:
		message = message + "There was a sqlite3 error. Here it is: {}".format(error)
		print(message)
	finally:
		await interaction.response.send_message(message, ephemeral=False)

@phrases.subcommand(description="Removes a phrase-response pair to the database (either by ID or name)")
async def drop(
	interaction: nextcord.Interaction,
	rowid: Optional[int] = SlashOption(description="The ID of the phrase in the database", required=False),
	phrase: Optional[str] = SlashOption(description="The phrase to give an autoresponse to", required=False),
):
	message = ""
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()
		
		findQuery = "select * from phrases"
		result = cursor.execute(findQuery)
		if(result is None):
			message = "Nothing was found in the database. Has it been /setup?"
		else:
			if(rowid is None and phrase is None):
				message = "Please specify an ID or an exact phrase to delete"
			else:
				deletionQuery = "DELETE FROM phrases WHERE "
				findQuery = "SELECT phrase FROM phrases WHERE "
				if(rowid is None):
					addition = "phrase='" + phrase +"'"
					deletionQuery = deletionQuery + addition
					findQuery = findQuery + addition
				else:
					addition = "rowid=" + str(rowid)
					deletionQuery = deletionQuery + addition
					findQuery = findQuery + addition

				result = cursor.execute(findQuery)
				res = result.fetchone()
				if(result is None or res is None):
					message = "The phrase was not found in the database. Use the list subcommand to make sure it's there."
				else:
					message = "Deleted ||" + res[0] + "|| from the phrase-response database"
					cursor.execute(deletionQuery)
					connection.commit()
	except sqlite3.Error as error:
		message = message + " There was a sqlite3 error. Here it is: {}".format(error)
		print(message)
	finally:
		await interaction.response.send_message(message, ephemeral=False)

@phrases.subcommand(description="Lists the phrase-response pairs in the database")
async def list(interaction: nextcord.Interaction):
	message = ""
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()
		
		findQuery = "select rowid, * from phrases"
		results = cursor.execute(findQuery)
		results = results.fetchall()

		message = "=====phrases and responses=====\n"
		for result in results:
			rowid = result[0]
			phrase = result[1]
			response = result[2]
			deletionVal = result[3]
			deletion = "yes"
			if(deletionVal == 0):
				deletion = "no"
			timeoutVal = result[4]
			timeout = ""
			if(timeoutVal == 0):
				timeout = "no"
			elif(timeoutVal == minute):
				timeout = "yes, a minute"
			elif(timeoutVal == hour):
				timeout = "yes, an hour"
			elif(timeoutVal == day):
				timeout = "yes, a day"
			else:
				timeout = "someone didn't sanitize their inputs! timeout: " + str(timeoutVal)
			message = message + "row: " + str(rowid) + " | phrase: " + phrase + " | response: " + response + " | delete: " + deletion + " | timeout: " + timeout + "\n"
		message = message + "=============================="
	except sqlite3.Error as error:
		message = message + " There was a sqlite3 error. Here it is: {}".format(error)
		print(message)
	finally:
		await interaction.response.send_message(message, ephemeral=False)