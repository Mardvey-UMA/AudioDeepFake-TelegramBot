import librosa
import librosa.display
import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
import random
from pydub import AudioSegment
import math
################################################################################################
def clean_temp(path):
    files = os.listdir(path)
    for f in files:
        s = f.split('.')
        if s[-1] != 'wav':
            os.remove(os.path.join(path, f))
################################################################################################
def predict(model, spec):
    classes = ['fake', 'real']
    test_image = cv2.imread(spec)
    test_image = cv2.resize(test_image, (224, 224))
    test_image = test_image / 255
    prediction = model.predict(np.array([test_image]))
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
################################################################################################
def make_spec(song_path, save_path):
    scale, sr = librosa.load(song_path)
    filter_banks = librosa.filters.mel(n_fft=2048, sr=22050, n_mels=128)
    mel_spectrogram = librosa.feature.melspectrogram(scale, sr=sr, n_fft=2048, hop_length=512, n_mels=128)
    log_mel_spectrogram = librosa.power_to_db(mel_spectrogram)
    fig = plt.figure(figsize=(3.5, 3.5))
    librosa.display.specshow(log_mel_spectrogram)
    plt.subplots_adjust(0, 0, 1, 1)
    n = [str(random.randint(0, 9)) for n in range(5)]
    spec_name = "".join(n)
    plt.savefig(save_path+ '/' + spec_name + '.png')
    return save_path+ '/' + spec_name + '.png'
################################################################################################
def convert_mp3(folder, file):
    src = folder + '/' + file
    dst = folder + '/' + file[:-4] + '.wav'
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")
    os.remove(src)
################################################################################################
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
################################################################################################
