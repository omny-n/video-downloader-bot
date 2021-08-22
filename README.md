# Telegram bot for downloading any videos

A simple telegram bot downloading any video writen in Python with [aiogram](https://github.com/aiogram/aiogram)

## Install 

The easiest way to run bot is with Docker:

```docker 
docker build -t bot .

docker run -d --restart=always --name bot -e TELEGRAM_API_TOKEN="the token for your bot" bot
```
