import nextcord, sqlite3, sys
from nextcord.ext import commands

sys.path.append("..")

intents = nextcord.Intents(
	guilds=True,guild_messages=True,guild_reactions=True,
	messages=True,message_content=True,
	reactions=True, 
	moderation=True)

client = nextcord.Client(intents=intents)
guild_ids=[]

@client.event
async def on_ready():
	await client.sync_all_application_commands()
	print("Hello!")

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

@client.slash_command(name="setup", description="sets up the bot. only run this once after a code update", guild_ids=[1191869544264900759])
async def setup(interaction: nextcord.Interaction):
	await setupTables()
	await populateGuildTable()
	await interaction.response.send_message("Done.", ephemeral=False)

async def setupTables():
	queries = []
	createChannelTableQuery = "CREATE TABLE IF NOT EXISTS channels(name TEXT UNIQUE, channelID INTEGER)"
	createGuildTableQuery = "CREATE TABLE IF NOT EXISTS guilds(guildID INTEGER UNIQUE)"

	queries.append(createChannelTableQuery)
	queries.append(createGuildTableQuery)

	for query in queries:
		await executeQuery(query)

async def populateGuildTable():
	guildSequence = client.guilds
	for guild in guildSequence:
		guildID = guild.id
		guild_ids.append(guildID)
		
		insertionQuery = "INSERT INTO guilds(guildID) VALUES({})".format(guildID)
		await executeQuery(insertionQuery)
