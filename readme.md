# Tournamentor (Discord)

Tournamentor is a small discord bot that should greatly help TO's of online tournaments. Tournamentor is meant as a supplement for tournament administration, not a replacement. The main problem it solves is confusion from tournament participants on what matches they should be playing.


# Commands
Here are the commands you can take advantage of with Tournamentor. Please be aware that you can only manage tournaments that the API Token owner has created.

## $set {challonge url}

    $set streetfighter5denver

This sets the current tournament. The challonge URL is set when you create the tournament on the web interface. This command needs to be run everytime you start the app.

![set command output](http://zak123.com/img/set-output.png)
## $status

This returns the current matches that participants should immediately start playing, and also upcoming matches that have someone waiting. If you'd like this to only return current matches, set `show_upcoming_matches` to no in the config. This command requires a set tournament using the `$set` command.

![status command output](http://zak123.com/img/status-output.png)
## $monitor

This continuously checks the status of a tournament every 15 seconds, and if an update is found, notifies the channel the same way that `$status` would. The refresh rate of 15 seconds is configurable with the config file, though be careful of rate limits on the Challonge API. This command requires a tournament be set with the `$set` command.

![enter image description here](http://zak123.com/img/monitor-output.png)
## $stop

This stops the $monitor command.

# Getting Started

Usage of this bot requires a small amount of technical know-how. I am working on an easier one click solution to add the bot to your own server, this update will be out before the release of Street Fighter 6. For now you'll have a little bit of work to get started.

 - Download this project as a zip from github. Near the top right is a green "Code" button, drop that down and click "download zip"
 - Download and install [Python](https://www.python.org/downloads/windows/). I have version 3.10.5, but the latest stable release should work fine as well. Just make sure its a recent version of python3. When installing, make sure to check the box to add Python to your windows PATH variables.
 - Open the Tournamentor code base you downloaded from github, and open this folder in terminal. If you are on windows 11, there should be an "Open in terminal" option if you right click the white space on file explorer. Make sure your terminal is running as admin.
 - In terminal, run the command `py get-pip.py` to install pip. If this fails, you can try other methods [here](https://pip.pypa.io/en/stable/installation/).
 - Once pip is installed, restart terminal in the project folder, make sure terminal is running as admin, and run ``pip install -r requirements.txt``
 - After pip downloads all the dependencies, its time to obtain our Discord and Challonge tokens.

**Obtaining your Challonge API key:**
- Log into Challonge.com on the web, navigate to https://challonge.com/settings/developer, click generate and voila.

**Obtaining your Discord API key:**
- Log into [Discords API application dashboard](https://discord.com/developers/applications).
- Once here, create a new app. Name it whatever you want. Add descriptions or whatever other info if you want, its not necessary.
- Navigate to the "Bot" tab on the left. Create a new bot user by clicking "Add Bot".
- Create your bot user, add whatever avatar you want, name it whatever, and click View Token. Copy this token and save it.
- Navigate to "Oauth2 -> URL Generator"
- Check "Bot" in the first box, a second box should appear, check "Admin". If you want to be more conservative with roles go ahead, I havent tested anything but Admin permissions yet.
- Copy the URL that is generated at the bottom, and navigate to it in a browser. It should ask you to add the bot to your server.

**Running the bot**
- Now that we have our API keys, its time to create a config file.
```
[Tokens]
challonge_username=zak123
challonge_api_key=THISISYOURCHALLONGEAPIKEY
discord_api_key=THISISYOURDISCORDAPIKEY

[ErrorMessages]
code_exception=Unexpected Error. Call Daigo for help!
permission_error_admin=Only admins can use this command.

[Options]
show_upcoming_matches=yes
auto_finalize_tournament_after_grand_finals=yes
command_prefix=$
monitor_refresh_interval=15
```
- Save this file as `config.ini` in the same folder as the code you downloaded from github, and edit the values to what you want.
- Open a terminal within the codes folder, and run `py app.py`

You should now see the bot become online in the member list of your discord, and commands should work. :)
