# Telegram Bot для выявления аудио DeepFake подделок
## Фреймворки
- pyTelegramBotAPI
- TensorFlow 2.8.0
- librosa
- pydub
- ffmpeg
- torch
- numpy 1.21.5
- matplotlib
## Команды
- **"/start"** - Приветственное сообщение и краткая инструкция по использованию бота
  - ![START](https://sun9-53.userapi.com/impf/AXzOpHG8cFLDb8IA-HVH9CC7GDgKtXspV4rOlQ/GXq_8Q38ei4.jpg?size=1080x1116&quality=95&sign=8d0aee0cce0b6295deef7d2d20967ff9&type=album)
- **"/help"** - Команда в случае, если пользователь не понял как работать с ботом
  - ![help](https://sun9-64.userapi.com/impf/WPhmy33EoVIqs197V27EP340QCnH1qByCaOhxQ/zjansI_IS5c.jpg?size=1080x514&quality=95&sign=534cbd84e3b7a46b30fd0ce653ef4ade&type=album)
- **"/info"** - Для получения дополнительной информации
  - ![info](https://sun9-64.userapi.com/impf/pn62dnk-_cc7XWdUkFh3ATY_MbW9rsZaOdP4eQ/_J7BRv6Xrg8.jpg?size=1073x881&quality=95&sign=c52c9c4adcae407db0db7ad1b3f06a24&type=album)
- В случае если введеный текст не является ни одной из вышеперечисленных команд, то бот выдаст предупредительное сообщение
  - ![error](https://sun9-29.userapi.com/impf/gD-1GFRn4MV_p53fGAExUhYJ-8HoipQTUKQUBA/FP43HBlkiZk.jpg?size=1080x357&quality=95&sign=d889732be0a3fdc2b5975c40b07f4a1b&type=album)
## Оценка аудиофайла
Для анализа вашего аудиофайла достаточно отправить файл формата .mp3 или .wav, далее бот сохранит вашу аудиозапись и ответит:

![answer](https://sun9-18.userapi.com/impf/9k8lyDKFzZH2pNVCbn1NbDHmFkj4c_kzOguSmQ/dQzpQh4sBNE.jpg?size=379x243&quality=95&sign=979c152786131724c0271707c3662946&type=album)

![wronganswer](https://sun9-84.userapi.com/impf/kfYmJgFJAQ5ZTlWGlu_XHTYrO50JUQwHyKHEqA/vg-Ikt0khHQ.jpg?size=356x241&quality=95&sign=6a07dd8adf4d730c6116d333cf28d617&type=album)

## Принцип работы
Для анализа аудиофайла бот использует нейронную сеть формата .h5 [Нейронная сеть для выявления DeepFake аудиозаписей](https://github.com/Mardvey-UMA/Neural-Network-for-AudioDeepFake-Detection) - Репозиторий обучения нейронной сети. Так как нейронная сеть обучалась на аудиозаписях длительностью 2 секунды, то она может анализировать файлы, только такой длительности, но если бот получит аудиофайл длительностью дольше двух секунд, то он разделит его на ранвые отрезки по 2 секунды.

Класс для разрезания аудифайлов, а также рассчёта их длительности в секундах
```python
class SplitWavAudio():
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename
        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 1000
        t2 = to_min * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(self.folder + '/' + split_filename, format="wav")

    def multiple_split(self, min_per_split):
        total_mins = math.ceil(self.get_duration())
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i + min_per_split, split_fn)
```
После разделения файла (если это потребуется) Бот преобразует каждый фрагмент в mel-спектрограмму

Функция для конвертации аудиофайла в mel-спектрограмму:
```python
def make_tensor(absolute_path):
    path = absolute_path
    scale, sr = librosa.load(path)
    filter_banks = librosa.filters.mel(n_fft=2048, sr=22050, n_mels=128)
    mel_spectrogram = librosa.feature.melspectrogram(scale, sr=sr, n_fft=2048, hop_length=512, n_mels=128)
    log_mel_spectrogram = librosa.power_to_db(mel_spectrogram)
    trch = torch.from_numpy(log_mel_spectrogram)
    if log_mel_spectrogram.shape != (10, 87):
        delta = 87 - log_mel_spectrogram.shape[1]
    trch = torch.nn.functional.pad(trch, (0, delta))
    np_arr = trch.cpu().detach().numpy()
    return np_arr
```
Для непосредственной оценки файла и предсказания его подлинности или нет используется следующая функция, которая принимает на вход веса модели, а также абсолютный путь до аудиозаписи и папку для сохранения спектрограммы
Функция возвращает 0 или 1 в случае если аудиозапись не подделана и если подделана соответственно
```python
def predskaz(model, audio_path, sv_path):
    classes = ['fake', 'real']
    name = str(random.randint(0, 1001)) + '.png'
    fig = plt.figure(figsize=(2.2464, 2.2464))
    librosa.display.specshow(make_tensor(audio_path))
    plt.subplots_adjust(0, 0, 1, 1)
    plt.savefig(sv_path + '/' + name)
    #print(sv_path + '/' + name)
    test_image = cv2.imread(sv_path + '/' + name)
    prediction = model.predict(np.array([test_image]))
    #print(prediction)
    a = str(prediction).replace("]", "").replace("[", "").replace(",", "")
    a = a.split()
    a1 = []
    for i in range(len(a)):
        a1.append(float(a[i]))
    maxarray = max(a1)
    index = a1.index(maxarray)
    if classes[index] == 'real':
        return 1
    if classes[index] == 'fake':
        return 0
```
Так как библиотека librosa, которая используется для конвертации аудиозаписей в mel-спектрограмму работает только с wav файлами, то для конвертации mp3 файлов описана функция их конвертации в wav формат
```python
def convert_mp3(folder, file):
    src = folder + '/' + file
    dst = folder + '/' + file[:-4] + '.wav'
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")
    os.remove(src)
```
Так как бот сохраняет все полученные аудиозаписи в папке для временных файлов, то чтобы не переполнять память создана функция для очищения папки от файлов изображений mel-спектрограмм
```python
def clean_temp(path):
    files = os.listdir(path)
    for f in files:
        s = f.split('.')
        if s[-1] != 'wav':
            os.remove(os.path.join(path, f))
```
## Структура проекта
- Файл **main.py** это основной алгоритм работы бота
- Файл **functions.py** вспомогательный файл для отдельного описания всех используемых функций
- Файл **config.py** конфигурационный файл, содержит токен бота, а также словарь с ответами на сообщения и пути для получения весов модели и папки с временными файлами
- Папка **'temp'** папка предназначенная для временных файло
- Папка **'model'** папка для хранения весов нейронной сети
## Контакты
- VK : [Матвей Раизнов](https://vk.com/maveyuma)
- [Telegram](https://t.me/barulitka)
- mail : chikernut213@gmai.com
