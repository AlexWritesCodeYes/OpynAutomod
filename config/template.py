import nextcord, sqlite3
from nextcord.ext import commands
from nextcord import SlashOption
from typing import Optional

from thebot import client, executeQuery, guild_ids

@client.slash_command(name="template", description="gets, sets, or syncs the server template", guild_ids=guild_ids)
async def template(interaction: nextcord.Interaction):
	pass

@template.subcommand(description="Gets the currently set server template, or a specific template by name")
async def get(interaction: nextcord.Interaction, name: Optional[str] = SlashOption(description="(optional) the name given to the template", required=False)):
	message = "The server template link is "
	templateLink = "not set! Try setting it with the 'set' subcommand."
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()
		findQuery = "SELECT url FROM template WHERE name="
		if(name == None):
			findQuery = findQuery + "'default'"
		else:
			findQuery = findQuery + "'" + name.lower() + "'"

		result = cursor.execute(findQuery)
		url = result.fetchone()

		if(result is not None and url is not None):
			templateLink = url[0]

		message = message + templateLink
		await interaction.response.send_message(message, ephemeral=False)
	except sqlite3.Error as error:
		logMessage = "There was a sqlite3 error. Here it is: {}".format(error)
		print(logMessage)
	finally:
		if(connection):
			cursor.close()
			connection.close()

@template.subcommand(description="Gets the currently set server template, or a specific template by name")
async def set(interaction: nextcord.Interaction, url: str = SlashOption(description="The new url for the template", required=True), name: str = SlashOption(description="(optional) a name to give your template", required=False)):
	if(url[:20] != "https://discord.new/"):
		await interaction.response.send_message("That is not a valid server template")

	if(name == None):
		name = "default"
	logMessage = "The " + name + " template was "
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()

		findQuery = "SELECT url FROM template WHERE name='" + name + "'"
		result = cursor.execute(findQuery)
		dbURL = result.fetchone()
		
		nextQuery = ""
		if(result is None or dbURL is None):
			print("no template under that name was found. creating it...")
			logMessage = logMessage + "not found, so it was created and set to " + url
			nextQuery = "INSERT INTO template(name, url) VALUES('" + name + "','" + url +  "')"
		else:
			logMessage = logMessage + "updated to " + url
			nextQuery = "UPDATE template SET url='" + url + "' WHERE name='" + name + "'"
		cursor.execute(nextQuery)
		connection.commit()
		cursor.close()
	except sqlite3.Error as error:
		logMessage = "There was a sqlite3 error. Here it is: {}".format(error)
		print(logMessage)
	finally:
		if(connection):
			connection.close()
		await interaction.response.send_message(logMessage, ephemeral=False)

@template.subcommand(description="Deletes a template (by name) from the database. Does not work on the default template")
async def drop(interaction: nextcord.Interaction, name: str = SlashOption(description="the name given to the template", required=True)):
	if(name is None):
		await interaction.response.send_message("Please enter the name of the template you wish to delete")
	elif(name.lower() == "default"):
		await interaction.response.send_message("Please use the update subcommand to change the default server template")
	else:
		try:
			connection = sqlite3.connect("everything.db")
			cursor = connection.cursor()

			findQuery = "SELECT url FROM template WHERE name='" + name + "'"
			result = cursor.execute(findQuery)

			nextQuery = ""
			if(result is None):
				await interaction.response.send_message("No template under that name was found. Use the list subcommand to see the template database contents")
			else:
				nextQuery = "DELETE FROM template WHERE name='" + name + "'"
			cursor.execute(nextQuery)
			connection.commit()
		except sqlite3.Error as error:
			logMessage = "There was a sqlite3 error. Here it is: {}".format(error)
			print(logMessage)
		finally:
			if(connection):
				cursor.close()
				connection.close()
			await interaction.response.send_message("The " + name + " template was deleted from the database")

@template.subcommand(description="Lists all templates in the database")
async def list(interaction: nextcord.Interaction):
	message = "=====Templates=====\n"
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()

		findQuery = "SELECT * FROM template"
		results = cursor.execute(findQuery)
		results = results.fetchall()
		
		for result in results:
			name = result[0]
			url = result[1]
			message = message + name + " | " + url + "\n"
		message = message + "==================="
	except sqlite3.Error as error:
		logMessage = "There was a sqlite3 error. Here it is: {}".format(error)
		print(logMessage)
	finally:
		if(connection):
			cursor.close()
			connection.close()
		await interaction.response.send_message(message, ephemeral=False)

@template.subcommand(description="Syncs the currently set server template, or a specific template by name")
async def sync(interaction: nextcord.Interaction, name: Optional[str] = SlashOption(description="(optional) the name given to the template", required=False)):
	if(name == None):
		name = "default"
	message = ""
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()

		findQuery = "SELECT url FROM template WHERE name='" + name + "'"
		result = cursor.execute(findQuery)
		url = result.fetchone()

		if(result is None or url is None):
			message = "The " + name + " server template is not set. Set it with the set subcommand"
		else:
			template = await client.fetch_template(url)
			await template.sync()
			message = "The " + name + " server template was synced."
		await interaction.response.send_message(message, ephemeral=False)
	except sqlite3.Error as error:
		logMessage = "There was a sqlite3 error. Here it is: {}".format(error)
		print(logMessage)
	finally:
		if(connection):
			cursor.close()
			connection.close()	