import nextcord
from nextcord.ext import commands

from thebot import client, guild_ids

@client.slash_command(name="delete", description="Deletes a welcome channel", guild_ids=guild_ids)
async def delete(interaction: nextcord.Interaction, channel: nextcord.abc.GuildChannel = None):
	channelName = channel.name
	if(channelName[:7] == 'welcome'):
		await channel.delete()
		await interaction.response.send_message("Succesfully deleted " + channelName, ephemeral=False)
	else:
		await interaction.response.send_message("That's not a welcome channel! Please do not do that.", ephemeral=False)