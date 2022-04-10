import telebot
import functions
import os
from config import temp, model, token, answers


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, answers['start_text1'])
        bot.send_message(message.from_user.id, answers['start_text2'])

    @bot.message_handler(commands=['help'])
    def help_message(message):
        bot.send_message(message.from_user.id, answers['help_text1'])

    @bot.message_handler(content_types=['text'])
    def error_message(message):
        if message.text == '/info':
            bot.send_message(message.from_user.id, answers['info'])
        elif (message.text != '/start') and (message.text != '/help'):
            bot.send_message(message.from_user.id, answers['error_text1'])


    @bot.message_handler(content_types=['document'])
    def wav_files(message):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = temp + '/' + message.document.file_name
        name = message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, answers['save_message'])
        flag = True
        if functions.SplitWavAudio(temp, name).get_duration() > 2:
            flag = False
            #print('duratin > 2')
        elif functions.SplitWavAudio(temp, name).get_duration() <= 2:
            flag = True
            #print('duratin <= 2')
        ans = 0
        if flag:
            audio_path = os.path.join(temp,name)
            #print(audio_path)
            ans = functions.predskaz(model,audio_path,temp)
            #print(audio_path)
            os.remove(audio_path)
            functions.clean_temp(temp)
        else:
            split_wav = functions.SplitWavAudio(temp, name)
            split_wav.multiple_split(min_per_split=2)
            os.remove(os.path.join(temp, name))
            functions.clean_temp(temp)
            names = os.listdir(temp)
            result = []
            for audio in names:
                #print(temp + '\\' + audio)
                if (functions.SplitWavAudio(temp, audio).get_duration()) < 2:
                    os.remove(os.path.join(temp, audio))
                    #print('duration<2')
                else:
                    audio_path = os.path.join(temp,audio)
                    result.append(functions.predskaz(model,audio_path,temp))
                    os.remove(audio_path)
                    functions.clean_temp(temp)
            #print(result)
            middle = sum(result) / len(result)
            if middle >= 0.5:
                ans = 1
            else:
                ans = 0

        if ans == 0:
            bot.send_message(message.from_user.id, answers['fake'])
        else:
            bot.send_message(message.from_user.id, answers['real'])

    @bot.message_handler(content_types=['audio'])
    def mp3_file(message):
        file_info = bot.get_file(message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = temp + '/' + message.audio.file_name
        name = message.audio.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, answers['save_message'])
        functions.convert_mp3(temp, name)
        name = name[:-4] + '.wav'
        flag = True
        if functions.SplitWavAudio(temp, name).get_duration() > 2:
            flag = False
        elif functions.SplitWavAudio(temp, name).get_duration() <= 2:
            flag = True
        ans = 0
        if flag:
            audio_path = os.path.join(temp,name)
            ans = functions.predskaz(model,audio_path,temp)
            os.remove(audio_path)
            functions.clean_temp(temp)
        else:
            split_wav = functions.SplitWavAudio(temp, name)
            split_wav.multiple_split(min_per_split=2)
            os.remove(os.path.join(temp, name))
            functions.clean_temp(temp)
            names = os.listdir(temp)
            result = []
            for audio in names:
                #print(temp + '/' + audio)
                if (functions.SplitWavAudio(temp, audio).get_duration()) < 2:
                    os.remove(os.path.join(temp, audio))
                    #print('duration<2')
                else:
                    audio_path = os.path.join(temp,audio)
                    result.append(functions.predskaz(model,audio_path,temp))
                    os.remove(audio_path)
                    functions.clean_temp(temp)
            #print(result)
            middle = sum(result) / len(result)

            if middle >= 0.5:
                ans = 1
            else:
                ans = 0

        if ans == 0:
            bot.send_message(message.from_user.id, answers['fake'])
        else:
            bot.send_message(message.from_user.id, answers['real'])

        # except Exception as e:
        #     #print(e)
        #     bot.reply_to(message, str(e))

    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    telegram_bot(token)
