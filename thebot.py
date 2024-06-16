import nextcord, sqlite3, sys, re
from nextcord.ext import commands
from datetime import datetime

sys.path.append("..")

intents = nextcord.Intents(
	guilds=True,guild_messages=True,guild_reactions=True,
	messages=True,message_content=True,
	reactions=True, 
	moderation=True)

client = nextcord.Client(intents=intents)
guild_ids=[]
minute = 60000
hour = 3600000
day = 86400000

phrases = set([])

@client.slash_command(name="setup", description="sets up the bot. only run this once after a code update", guild_ids=[1191869544264900759])
async def setup(interaction: nextcord.Interaction):
	await setupTables()
	await populateGuildTable()
	await updateLocalLists()
	await interaction.response.send_message("Done.", ephemeral=False)

@client.event
async def on_ready():
	#await client.sync_all_application_commands()
	await client.register_new_application_commands()
	await client.sync_application_commands(guild_id=1191869544264900759)
	print("Hello!")

@client.event
async def on_message(message: nextcord.Message):
	if(message.author.bot is not True):
		splitup = message.content.lower().split(' ')
		splitupSet = set([])
		for word in splitup:
			splitupSet.add(re.sub(r'[.,\/#!?$%\^&\*;:{}=\-_`~()]', '', word))

		if(len(phrases) == 0):
			print("no phrases in the list")
		for phrase in phrases:
			if(await phraseFinder(splitupSet, phrase)):
				print("Found a phrase!")
				try:
					connection = sqlite3.connect("everything.db")
					cursor = connection.cursor()
					findQuery = "SELECT response,deletion,timeout FROM phrases WHERE phrase='" + phrase + "'"
					result = cursor.execute(findQuery)
					result = result.fetchone()
					reply = result[0]
					deletion = result[1]
					timeout = result[2]

					await message.reply(reply)

					logMessage = "A user posted the word or phrase ||"+ phrase + "|| in " + message.channel.name + "."
					if(deletion == 1 and timeout > 0):
						duration = None
						reason = "posting a banned phrase"
						if(timeout == minute):
							duration = datetime.timedelta(minutes=1)
						elif(timeout == hour):
							duration = datetime.timedelta(hours=1)
						elif(timeout == day):
							duration = datetime.timedelta(days=1)

						await message.author.timeout(duration, reason=reason)
						await message.delete()
						logMessage = logMessage + " The message containing it was deleted and the user who posted it was timed out."
					elif(deletion == 1):
						await message.delete()
						logMessage = logMessage + "The message containing it was deleted."
					elif(timeout > 0):
						duration = None
						reason = "posting a banned phrase"
						if(timeout == minute):
							duration = datetime.timedelta(minutes=1)
						elif(timeout == hour):
							duration = datetime.timedelta(hours=1)
						elif(timeout == day):
							duration = datetime.timedelta(days=1)

						await message.author.timeout(duration, reason=reason)
						logMessage = logMessage + " The user who posted the message was timed out."
				except sqlite3.Error as error:
					logMessage = logMessage +  " There was a sqlite3 error. Here it is: {}".format(error)
				finally:
					try:
						findLogChannelQuery = "SELECT channelID FROM channels WHERE name='log'"
						result = cursor.execute(findLogChannelQuery)
						result = result.fetchone()
						channelID = result[0]
						if(channelID is not None):
							channel = message.guild.get_channel(channelID)
							await channel.send(logMessage)
						else:
							print("No log channel has been set yet")
					except sqlite3.Error as error:
						logMessage = logMessage +  " There was a sqlite3 error. Here it is: {}".format(error)
					finally:
						print(logMessage)
						cursor.close()
						if(connection):
							connection.close()
	else:
		print("bot message")

async def phraseFinder(wordList, phrase):
	splitphrase = phrase.split(' ')
	phraseLength = len(splitphrase)
	if(phraseLength > 1):
		firstIndex = 0
		lastIndex = phraseLength - 1

		foundit = False
		while(lastIndex < len(wordList)):
			if(wordList[firstIndex] == splitphrase[0]):
				breakCondition = False
				for i in range(1, phraseLength):
					if(wordList[firstIndex + i] != splitphrase[i]):
						breakCondition = True
					if(breakCondition):
						break
				if(not breakCondition):
					foundit = True
			if(foundit is True):
				return foundit
			
			firstIndex = firstIndex + 1
			lastIndex += lastIndex + 1
		if(not foundit):
			return foundit
	else:
		return phrase in wordList

async def executeQuery(query):
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()
		result = cursor.execute(query)
		connection.commit()
		print("executed query: " + query)
		cursor.close()
	except sqlite3.Error as error:
		print("There was a sqlite3 error. Here it is: ", error)
	finally:
		if(connection):
			connection.close()

async def updateLocalLists():
	message = ""
	try:
		connection = sqlite3.connect("everything.db")
		cursor = connection.cursor()

		phraseQuery = "SELECT * FROM phrases"
		result = cursor.execute(phraseQuery)
		results = result.fetchall()
		for result in results:
			print("adding: " + result[0])
			phrases.add(result[0])
		print(str(len(phrases)) + " in the phrases list")

		cursor.close()
	except sqlite3.Error as error:
		print("There was a sqlite3 error. Here it is: ", error)
	finally:
		if(connection):
			connection.close()

async def setupTables():
	queries = []
	createChannelTableQuery = "CREATE TABLE IF NOT EXISTS channels(name TEXT UNIQUE, channelID INTEGER)"
	createGuildTableQuery = "CREATE TABLE IF NOT EXISTS guilds(guildID INTEGER UNIQUE)"
	createTemplateTableQuery = "CREATE TABLE IF NOT EXISTS template(name TEXT UNIQUE, url TEXT)"
	createPhrasesTableQuery = "CREATE TABLE IF NOT EXISTS phrases(phrase TEXT UNIQUE, response TEXT, deletion INT, timeout INT)"

	queries.append(createChannelTableQuery)
	queries.append(createGuildTableQuery)
	queries.append(createTemplateTableQuery)
	queries.append(createPhrasesTableQuery)

	for query in queries:
		await executeQuery(query)

async def populateGuildTable():
	guildSequence = client.guilds
	for guild in guildSequence:
		guildID = guild.id
		guild_ids.append(guildID)
		
		insertionQuery = "INSERT INTO guilds(guildID) VALUES({})".format(guildID)
		await executeQuery(insertionQuery)
