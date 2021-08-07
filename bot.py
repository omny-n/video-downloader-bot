import os
import functools
import logging
import traceback
import tempfile
import re
from typing import NamedTuple
import asyncio
from asyncio.exceptions import TimeoutError

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatActions, ChatType
from aiogram.utils import exceptions

import youtube_dl
from youtube_dl.utils import DownloadError


class Video_response(NamedTuple):
    """Response structure of the downloaded video"""
    filepath: str
    error: str


if not os.getenv("TELEGRAM_API_TOKEN"):
    exit("Error: no token provided. Terminated.")
bot = Bot(token=os.getenv("TELEGRAM_API_TOKEN"))
logging.basicConfig(level=logging.INFO)
dp = Dispatcher(bot)


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))
    return inner

@run_in_executor
def download_video(url, tempdir: str) -> Video_response:
    logging.info("Downloading for %s", url)
    ydl_opts = {
      "outtmpl": f"{tempdir}/%(id)s.%(ext)s",
      "noplaylist": True,
      "verbose": True,
    }
    success = None
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        success = True
    except (DownloadError, TimeoutError):
        err = traceback.format_exc()
        logging.error("Download failed for %s ", url)
        success = False  
    
    if success:
        return Video_response(filepath = os.path.join(tempdir, [i for i in os.listdir(tempdir)][0]), 
                              error = None)
    else:
        return Video_response(filepath=None,
                              error = err)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Hi!\nI'm VideoDownloader Bot\n"
                        "Just send me link to any video and I'll download it for you")

@dp.message_handler(commands=['help', 'about'])
async def about(message: types.Message):
    await message.reply("CuteDownloader by @Omny_N\n"
                        "GitHub: https://github.com/omny-n/video-downloader-bot")

@dp.message_handler(text_startswith=['https://'], chat_type=ChatType.PRIVATE)
@dp.message_handler(text_startswith=['/download'])
async def video(message: types.Message):
    url = re.sub(r'/download\s*', '', message.text)
    if not re.findall(r"^https?://", url.lower()):
        await message.reply("It's not a link :(")
        return
    
    temp_dir = tempfile.TemporaryDirectory()
    answer = await message.reply("Downloading...")
    result = await download_video(url, temp_dir.name)
    if result.error == None:
        await answer.edit_text("Download complete! Sending now...")
        await bot.send_chat_action(message.from_user.id, ChatActions.UPLOAD_VIDEO)
        
        try:
            with open(result.filepath, 'rb') as video:
                await message.answer_video(video=video)

                await answer.edit_text("Download success!")
            
        except exceptions.NetworkError:
            await answer.edit_text("Download failed. File is large :(")
    else:
        await answer.edit_text("Download failed. Check your link or try again.")

    temp_dir.cleanup()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

