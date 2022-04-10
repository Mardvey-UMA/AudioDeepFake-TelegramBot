import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from tensorflow.keras.models import load_model
token = '###################################'
model_path = '/home/telegram_bot/model/auidiofaker.h5'
temp = '/home/telegram_bot/temp'
model = load_model(model_path)
answers = {
            'start_text1': 'Привет, я бот, который поможет тебе определить подлинность твоего аудиофайла',

           'start_text2': 'У бота такие правила:'
             '\nИмей терпение, бот обработает аудиозапись не сразу'
             '\nБот распознает DeepFake подделки речи на английском языке'
             '\nРазмер твоего файла не должен превышать 50мб'
             '\nБот обрабатывает файлы формата .mp3 и .wav'
             '\nВведи команду /help для более подробной инструкции'
             '\nВведи команду /info для дополнительной информации о боте',

           'help_text1':'Краткая инструкция по применению бота:'
              '\n1.Пришли свой аудиофайл'
              '\n2.Дождись, когда бот сохранит и обработает его'
              '\n3.Наслаждайся результатом',

           'error_text1': 'Извини, я тебя не понимаю, введи "/help", чтобы получить инструкцию для бота',
            'save_message': 'Я принял и сохранил твой файл',
            'fake': 'Я думаю это подделка',
            'real': 'Я думаю это настоящая аудизапись',
            'info': 'Контакты:'
                    '\nVK - https://vk.com/maveyuma'
                    '\nTelegram - https://t.me/barulitka'
                    '\nmail - chikernut213@gmail.com'
                    '\nБот для выявления DeepFake аудиозаписей, с помощью нейронной сети'
                    '\nGitHub - https://github.com/Mardvey-UMA/AudioDeepFake-TelegramBot'
            }

