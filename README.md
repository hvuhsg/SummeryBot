# SummeryBot
Telegram bot that will summarize the conversation at any point for easy joining.
Just add the bot to your group and that it.
https://t.me/SummySumBot

## Quick start
With Docker
```commandline
docker run yoyocode/summybot:latest -e BOT_TOKEN=<BOT_TOKEN> -e OPENAI_KEY=<OPENAI_API_KEY>
```

Without Docker
1. download repo
```commandline
git clone https://github.com/hvuhsg/SummeryBot.git
```
2. install requirements
```commandline
pip install -r requirements.txt
```
3. run bot
```commandline
python -m bot
```


## Example
![group chat](/images/Screenshot%20from%202023-05-10%2000-55-31.png)
![chat summary](/images/Screenshot%20from%202023-05-10%2000-56-23.png)