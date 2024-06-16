import nextcord, sqlite3
from nextcord.ext import commands
from nextcord import SlashOption
from typing import Optional

from thebot import client, guild_ids, minute, hour, day

@client.slash_command(name="responses", description="gets or modifies a response in the phrase-response system", guild_ids=guild_ids)
async def responses(interaction: nextcord.Interaction):
	pass

@responses.subcommand(description="Retrieves a response from the phrase-response database (either by ID or phrase)")
async def get(
	interaction: nextcord.Interaction,
	rowid: Optional[int] = SlashOption(description="The ID of the phrase in the database", required=False),
	phrase: Optional[str] = SlashOption(description="The phrase as it exists in the database", required=False),
):
	message = ""
	if(rowid is None and phrase is None):
		message = "Please select either the exact phrase or its ID to get a response"
		await interaction.response.send_message(message, ephemeral=True)
	else:
		try:
			connection = sqlite3.connect("everything.db")
			cursor = connection.cursor()
			
			findQuery = "select * from phrases"
			result = cursor.execute(findQuery)
			if(result is None):
				message = "Nothing was found in the database. Has it been /setup?"
			else:
				findQuery = "SELECT * FROM phrases WHERE "
				if(rowid is None):
					addition = "phrase='" + phrase +"'"
					findQuery = findQuery + addition
				else:
					addition = "rowid=" + str(rowid)
					findQuery = findQuery + addition
				result = cursor.execute(findQuery)
				response = result.fetchone()
				if(response is None):
					message = "The requested phrase entry was not found. Use /phrases list to see if it's there."
				else:
					message = "phrase: ||" + response[0] + "|| | reply: " + response[1] + " | response: "
					if(response[2] == 0):
						message = message + "don't "
					message = message + "delete the message and "
					if(response[3] == 0):
						message = message + "don't "
					message = message + "time out the user who posted the containing message"
					if(response[3] != 0):
						message = message + " for a"
						if(response[3] == minute):
							message = message + " minute."
						elif(response[3] == hour):
							message = message + "n hour."
						elif(response[3] == day):
							message = message + " day."
						else:
							message = message + "n amount of time that the dev forgot to program."
			cursor.close()
		except sqlite3.Error as error:
			message = message + "There was a sqlite3 error. Here it is: {}".format(error)
			print(message)
		finally:
			await interaction.response.send_message(message, ephemeral=False)

@responses.subcommand(description="Modifies a response from the phrase-response database (either by ID or phrase)")
async def modify(
	interaction: nextcord.Interaction,
	rowid: Optional[int] = SlashOption(description="The ID of the phrase in the database", required=False),
	phrase: Optional[str] = SlashOption(description="The phrase as it exists in the database", required=False),
	newreply: Optional[str] = SlashOption(description="(optional) The new reply for the phrase", required=False),
	deletion: Optional[bool] = SlashOption(
		description="(optional) Delete the message containing the phrase?",
		choices={"Yes": True, "No": False},
		required=False
		),
	timeout: Optional[int] = SlashOption(
		description="(optional) Time the user who posted the phrase out?",
		choices={"No": 0, "Yes, for a minute": minute, "Yes, for an hour": hour, "Yes, for a day": day},
		required=False
		),
):
	message = "Updated: ["
	if(rowid is None and phrase is None):
		message = "Please select either the exact phrase or its ID to get a response"
		await interaction.response.send_message(message, ephemeral=True)
	else:
		try:
			connection = sqlite3.connect("everything.db")
			cursor = connection.cursor()

			updateQuery = ""
			if(newreply is not None):
				updateQuery = "UPDATE phrases SET "
				updateQuery = updateQuery + "response='" + newreply + "' WHERE "
				if(rowid is not None):
					updateQuery = updateQuery + "rowid=" + str(rowid)
				else:
					updateQuery = updateQuery + "phrase=" + phrase

				cursor.execute(updateQuery)
				connection.commit()
				message = message + " reply "
			if(deletion is not None):
				updateQuery = "UPDATE phrases SET "
				deletionVal = 0
				if(deletion == 1):
					deletionVal = 1
				updateQuery = updateQuery + "deletion='" + str(deletionVal) + "' WHERE "
				if(rowid is not None):
					updateQuery = updateQuery + "rowid=" + str(rowid)
				else:
					updateQuery = updateQuery + "phrase=" + phrase

				cursor.execute(updateQuery)
				connection.commit()
				message = message + " deletion "
			if(timeout is not None):
				updateQuery = "UPDATE phrases SET timeout='" + str(timeout) + "' WHERE "
				if(rowid is not None):
					updateQuery = updateQuery + "rowid=" + str(rowid)
				else:
					updateQuery = updateQuery + "phrase=" + phrase
				cursor.execute(updateQuery)
				connection.commit()
				message = message + " timeout "
			message = message + "]"
			cursor.close()
		except sqlite3.Error as error:
			message = message + " There was a sqlite3 error. Here it is: {}".format(error)
			print(message)
		finally:
			await interaction.response.send_message(message, ephemeral=False)