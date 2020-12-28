from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import numpy as np
from PIL import Image
import seam_carving
from dotenv import load_dotenv
load_dotenv()
import os

TOKEN = os.getenv("TOKEN")

distort_percent = 50
queueNum = 0

updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id, text="Просто отправь мне фотку, если я не отвечаю - значит я сейчас занят или выключен и обработаю твою фотку чуть позже")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def distort(update, context):
  queueNum = False
  queueNum = queueNum + 1

  print('got new photo; queue: ' + str(queueNum))

  context.bot.send_message(chat_id=update.effective_chat.id, text='Обрабатываю твою фотку')

  file = context.bot.getFile(update.message.photo[-1].file_id)
  filename = update.message.photo[-1].file_id + '.jpg'
  file.download('./raw/' + filename)

  src = np.array(Image.open('./raw/' + filename))
  src_h, src_w, _ = src.shape
  dst = seam_carving.resize(
    src, (src_w - (src_w / 100 * distort_percent), src_h - (src_h / 100 * distort_percent)),
    energy_mode='backward',   # Choose from {backward, forward}
    order='width-first',  # Choose from {width-first, height-first}
    keep_mask=None
  )

  Image.fromarray(dst).save('./result/' + filename)

  context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('./result/' + filename, 'rb'))

  queueNum = queueNum - 1

  print('finished photo; queue: ' + str(queueNum))

image_handler = MessageHandler(Filters.photo, distort)
dispatcher.add_handler(image_handler)

updater.start_polling()