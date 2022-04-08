import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from tensorflow.keras.models import load_model
token = '#####################################'
model_path = '/home/telegram_bot/model/amatory.h5'
temp = '/home/telegram_bot/temp'
model = load_model(model_path)