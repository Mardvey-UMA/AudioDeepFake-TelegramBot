import telebot
import functions
import os
from config import temp,model,token

def telegram_bot(token):
    bot = telebot.TeleBot(token)
    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, 'Привет, я бот, который поможет тебе определить подлинность твоего аудиофайла')
    @bot.message_handler(content_types=['document', 'audio', 'text'])
    def get_message(message):
        try:
            if message.content_type == 'text':
                if message.text == '/start':
                    bot.send_message(message.from_user.id,
                                     'Привет, я бот, который поможет тебе определить подлинность твоего аудиофайла')
                    bot.send_message(message.from_user.id,
                                     'Давай начнем, у бота такие правила:'
                                     '\nИмей терпение, бот обработает аудиозапись не сразу'
                                     '\nБот распознает DeepFake подделки речи на английском языке'
                                     '\nРазмер твоего файла не должен превышать 50мб'
                                     '\n Введи команду /help для более подробной инструкции')
                elif message.text == '/help':
                    bot.send_message(message.from_user.id, 'Краткая инструкция по применению бота:'
                                                           '\n1.Пришли свой аудиофайл'
                                                           '\n2.Дождись, когда бот сохранит и обработает его'
                                                           '\n3.Наслаждайся результатом')
                else:
                    bot.send_message(message.from_user.id,
                                     'Извини, я тебя не понимаю, введи "/help", чтобы получить инструкцию для бота')
            elif (message.content_type == 'document') or (message.content_type == 'audio'):
                if message.content_type == 'document':
                    file_info = bot.get_file(message.document.file_id)
                elif message.content_type == 'audio':
                    file_info = bot.get_file(message.audio.file_id)

                downloaded_file = bot.download_file(file_info.file_path)

                if message.content_type == 'document':
                    src = temp + '/' + message.document.file_name
                    name = message.document.file_name
                elif message.content_type == 'audio':
                    src = temp + '/' + message.audio.file_name
                    name = message.audio.file_name

                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)

                bot.reply_to(message, "Я принял и сохранил твой файл")

                if message.content_type == 'audio':
                    functions.convert_mp3(temp,name)
                    name = name[:-4]+'.wav'

                flag = True

                if (functions.SplitWavAudio(temp,name).get_duration() > 2):
                    flag = False
                elif (functions.SplitWavAudio(temp,name).get_duration() <= 2):
                    flag = True
                ans = 0
                if flag:
                    spec_path = functions.make_spec(os.path.join(temp,name),temp)
                    pr = functions.predict(model,spec_path)
                    ans = pr
                    os.remove(os.path.join(temp,name))
                    functions.clean_temp(temp)
                else:
                    split_wav = functions.SplitWavAudio(temp, name)
                    split_wav.multiple_split(min_per_split=2)
                    os.remove(os.path.join(temp,name))
                    functions.clean_temp(temp)
                    names = os.listdir(temp)
                    result = []
                    for audio in names:
                        print(temp +'\\'+ audio)
                        if (functions.SplitWavAudio(temp,audio).get_duration()) < 2:
                            os.remove(os.path.join(temp,audio))
                        else:
                            spec_path = functions.make_spec(os.path.join(temp,audio),temp)
                            result.append(functions.predict(model,spec_path))
                            os.remove(os.path.join(temp,audio))
                            os.remove(spec_path)
                    print(result)
                    middle = sum(result)/len(result)
                    if middle >= 0.5:
                        ans = 1
                    else:
                        ans = 0
                if ans == 0:
                    bot.send_message(message.from_user.id,'Я думаю это подделка')
                else:
                    bot.send_message(message.from_user.id,'Я думаю это настоящая аудизапись')
        except Exception as e:
            print(e)
            bot.reply_to(message, str(e))
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    telegram_bot(token)

