import librosa
import librosa.display
import numpy as np
import os
import cv2
import torch
import torch.nn.parallel
import torch.optim
import torch.utils.data
import torch.utils.data.distributed
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
################################################################################################
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
