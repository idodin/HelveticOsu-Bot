# HelveticOsu Bot
[![Python](https://img.shields.io/badge/Python-3.4-brightgreen.svg)](https://www.python.org/downloads/)
[![Discord](https://img.shields.io/discord/124944592922476546.svg)](https://discordapp.com/invite/unhFVG6)

This bot is created for use on the Swiss osu! community discord. 

## Dependencies

* [discord.py](https://github.com/Rapptz/discord.py)
* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
* [requests](https://pypi.python.org/pypi/requests/)

You may install dependencies via `python3 -m pip install --user -r requirements.txt` 

## Installation
To run a bot on discord, you'll have to [create a bot account](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).

Before continuing, in your terminal, export your Discord token as an environment variable. (Or edit your PATH variable on Windows.)
```
$ export DISCORD_TOKEN='your-token-here'
```
You will have to do this each time you restart your shell.

## Notes and acknowledgements
This project is largely inspired by the [McGill Discord Martlet bot](https://github.com/Adoria/Martlet)

This project also uses the osu! API. [Read the documentation for more information](https://github.com/ppy/osu-api/wiki) on that project.

Many thanks to JanDark / Adoria for his explanations on his code! 