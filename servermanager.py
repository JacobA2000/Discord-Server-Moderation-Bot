import discord
from discord.ext import commands

import json
import re
import os
from datetime import datetime

#FUNCTION:    msg_contains_word()
#ARGUEMENTS:  String msg, String word
#RETURNS:     Bool
#DESCRIPTION: Search for a specific word in a string using regular expressions 
#             to detect if it is a word rather than a sequence of characters.
def msg_contains_word(msg, word):
    return re.search(fr'\b({word})\b', msg) is not None

#Checking if the config.json file exists and if not creating it.
if os.path.exists("./config.json"):
    pass
else:
    print("Creating blank config.json file please open it, add your token and restart the bot.")
    configJsonTemplate = {"token": "", "prefix": "$", "dateFormat": "%d-%m-%Y, %H:%M", "bannedWords": [], "adminBannedWordBypass": False}

    with open("./config.json", "w+") as f:
        json.dump(configJsonTemplate, f)

#Getting config data from json
with open("./config.json") as f:
    configData = json.load(f)

token = configData["token"]
prefix = configData["prefix"]
dateFormat = configData["dateFormat"]
bannedWords = configData["bannedWords"] 
adminBannedWordBypass = configData["adminBannedWordBypass"]

#Creating the bot object
bot = commands.Bot(command_prefix= f"{prefix}")

#Remove the default help command to allow us to create our own
bot.remove_command("help")

#FUNCTION:    on_ready()
#ARGUEMENTS:  None
#RETURNS:     Nothing
#DESCRIPTION: Do something when bot is ready.
@bot.event
async def on_ready():
    print("Bot is online.")
    #Change bot's activity
    await bot.change_presence(activity=discord.Game(name=f"{prefix}, Help: {prefix} help"))

#FUNCTION:    on_ready()
#ARGUEMENTS:  Discord.message message
#RETURNS:     Nothing
#DESCRIPTION: Do something when a message is recieved. 
@bot.event
async def on_message(message):
    messageAuthor = message.author
    authorIsAdmin = messageAuthor.guild_permissions.administrator

    #Profanity filter
    if bannedWords != None:
        if adminBannedWordBypass == False or authorIsAdmin == False:
            for bannedWord in bannedWords:
                if msg_contains_word(message.content.lower(), bannedWord):
                    await message.delete()
                    await message.channel.send(f"{messageAuthor.mention} your message has been removed as it contains a banned word.")
    
    #Allow commands to be processed despite the custom on_message event
    await bot.process_commands(message)

#FUNCTION:    serverinfo()
#ARGUEMENTS:  Discord.context ctx
#RETURNS:     Nothing
#DESCRIPTION: Retrieves info about the current server and 
#             sends it back as an embed message.
@bot.command()
async def serverinfo(ctx):
    server = ctx.guild
    numVoiceChannels = len(server.voice_channels)
    numTextChannels = len(server.text_channels)
    numChannels = numVoiceChannels + numTextChannels

    roles = list(server.roles)
    roles = reversed(roles)
    rolesString = ""
    for role in roles:
        rolesString += f"{role.name}, " 

    emojis = server.emojis
    emojiString = ""
    for emoji in emojis:
        emojiString += str(emoji)

    timeNow = datetime.utcnow()
    serverAge = timeNow - server.created_at
    serverAgeInS = serverAge.total_seconds()
    serverAgeYears = divmod(serverAgeInS, 31536000)
    serverAgeDays = divmod(serverAgeYears[1], 86400)
    serverAgeHours = divmod(serverAgeDays[1], 3600)
    serverAgeMinutes = divmod(serverAgeHours[1], 60)
    serverAgeString = f"({int(serverAgeYears[0])} years, {int(serverAgeDays[0])} days, {int(serverAgeHours[0])} hours, {int(serverAgeMinutes[0])} minutes ago)"
    
    embed=discord.Embed(title="SERVER INFO", description="Here is the info I could retrieve for this server: ", color=0x000000)
    embed.set_thumbnail(url=server.icon_url)
    embed.add_field(name="NAME:", value=server.name, inline=True)
    embed.add_field(name="ID:", value=server.id, inline=True)
    embed.add_field(name="OWNER:", value=f"{server.owner}", inline=True)
    embed.add_field(name="REGION:", value=server.region, inline=True)
    embed.add_field(name="MEMBERS:", value=server.member_count, inline=True)
    embed.add_field(name="MEMBERS BOOSTING:", value=server.premium_subscription_count, inline=True)
    embed.add_field(name="ROLES:", value=rolesString[:-2], inline=False)
    embed.add_field(name="SERVER CHANNELS:", value=f"{numChannels} channels ({numTextChannels} text, {numVoiceChannels} voice)", inline=False)
    embed.add_field(name="SERVER CREATED:", value=f"{server.created_at.strftime(dateFormat)} UTC {serverAgeString}", inline=False)
    await ctx.send(embed=embed)
    if len(emojis) > 0:
        await ctx.send("**Server Custom Emojis:**\n" + emojiString)
    else:
        await ctx.send("**Server Custom Emojis:**\nNo custom emojis.")

    #await ctx.message.delete()

#FUNCTION:    userinfo()
#ARGUEMENTS:  Discord.context ctx, String name
#RETURNS:     Nothing
#DESCRIPTION: Retrieves info about the command author or specified user in the current server and 
#             sends it back as an embed message.
@bot.command()
async def userinfo(ctx, name=""):
    #If an arguement for name is passed search for that user.
    if name != "":
        user = ctx.guild.get_member_named(name)
    else:
        user = ctx.author

    #Get user's primary activity
    if user.activity != None:
        userActivity = user.activity.name
    else:
        userActivity = "Nothing"

    #Get a list of roles in the order of rank heirarchy (highest role first)
    roles = list(user.roles)
    roles = reversed(roles)
    #Get a string containing every role name seperated by a coma.
    rolesString = ""
    for role in roles:
        rolesString += f"{role.name}, " 

    if user != None:
        embed=discord.Embed(title="USER INFO", description="Here is the info I could retrieve for this user: ", color=user.colour)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="NAME:", value=user.name, inline=True)
        embed.add_field(name="NICKNAME:", value=user.nick, inline=True)
        embed.add_field(name="ID:", value=user.id, inline=True)
        embed.add_field(name="CREATED:", value=f"{user.created_at.strftime(dateFormat)} UTC", inline=True)
        embed.add_field(name="JOINED:", value=f"{user.joined_at.strftime(dateFormat)} UTC", inline=True)
        embed.add_field(name="STATUS:", value=user.status, inline=True)
        embed.add_field(name="PLAYING:", value=userActivity, inline=True)
        embed.add_field(name="ROLES:", value=rolesString[:-2], inline=True)
        embed.add_field(name="TOP ROLE:", value=user.top_role.name, inline=True)
        embed.add_field(name="IS BOT:", value=user.bot, inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"User {name} is not a member of this server. Please check your spelling and capitalisation of the name. If the name is more than one word please encapsulate it in qoutation marks e.g. \"multi word name\".")

#FUNCTION:    addbannedword()
#ARGUEMENTS:  Discord.context ctx, String wordToAdd
#RETURNS:     Nothing
#DESCRIPTION: Adds a new word to the bannedWords list and the config.json file.     
@bot.command()
@commands.has_permissions(administrator=True)
async def addbannedword(ctx, wordToAdd):
    #Check if the word is already banned
    if wordToAdd.lower() in bannedWords:
        await ctx.send("That word is already banned.")
    else:
        #Append wordToAdd to the end of the bannedWords list
        bannedWords.append(wordToAdd.lower())

        #Update the config.json file to include the new banned word
        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
        
        #Delete the command authors message to hide the word.
        await ctx.message.delete()
        await ctx.send("Word has been added to the banned words. Your initial message has also been deleted.")

#FUNCTION:    removebannedword()
#ARGUEMENTS:  Discord.context ctx, String wordToRemove
#RETURNS:     Nothing
#DESCRIPTION: Remove a word from the bannedWords list and the config.json file.     
@bot.command()
@commands.has_permissions(administrator=True)
async def removebannedword(ctx, wordToRemove):
    #Check if the word is in the bannedWords list
    if wordToRemove.lower() in bannedWords:
        #Remove wordToRemove from the bannedWords list
        bannedWords.remove(wordToRemove.lower())

        #Remove wordToRemove from the config.json file
        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
        
        #Delete the command authors message to hide the word.
        await ctx.message.delete()
        await ctx.send("Word has been removed from the banned words. Your initial message has also been deleted.")
    else:
        await ctx.send("That word isn't currently banned.")

#FUNCTION:    adminwordbanbypass()
#ARGUEMENTS:  Discord.context ctx, String enableBypass
#RETURNS:     Nothing
#DESCRIPTION: Changes whether or not admins are allowed to use banned words.     
@bot.command()
@commands.has_permissions(administrator=True)
async def adminwordbanbypass(ctx, enableBypass):
    bypassBool = None

    #Convert the string enableBypass to the bool bypassBool
    if enableBypass.lower() == "true":
        bypassBool = True
    elif enableBypass.lower() == "false":
        bypassBool = False
    else:
        await ctx.send("That is not a valid parameter, adminwordbanbypass only takes values of true or false.")

    if bypassBool != None:
        #Change the global variable adminBannedWordBypass to the value of bypassBool
        global adminBannedWordBypass
        adminBannedWordBypass = bypassBool

        #Edit the value of adminBannedWordBypass in the json file 
        with open("./config.json", "r+") as f:
                data = json.load(f)
                data["adminBannedWordBypass"] = bypassBool
                f.seek(0)
                f.write(json.dumps(data))
                f.truncate()

#FUNCTION:    removebannedword()
#ARGUEMENTS:  Discord.context ctx, Int amount
#RETURNS:     Nothing
#DESCRIPTION: Clears X amount of messages from the current channel, where X = the amount parameter.     
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=10):
    amount += 1
    await ctx.channel.purge(limit=amount)

if token != "":
    bot.run(token)
else:
    print("Token not added please add it in the config.json!")