import os
import sys

import pandas as pd
# from fastapi import FastAPI, UploadFile
import pickle
sys.path.append("../")
from scripts.helpers import *
from scripts.logspectrogram import *
from scripts.models import *
from scripts.predict import *
from scripts.tokenizer import *

class Model(self):
    def __init__(self):

        # load files
        meta_data = pd.read_csv("../data/meta_data.csv")
        sorted_metadata = meta_data.sort_values(by="duration")
        labels = sorted_metadata["label"].to_list()
        translation_obj = read_obj("../data/translation_dict.pkl")

        # load translation
        translations = []
        for label in labels:
            translations.append(translation_obj[label])

        # init tokenizer
        tokenizer = Tokenizer(translations)
        int_to_char, char_to_int = tokenizer.build_dict()
        output_dim = len(char_to_int) + 2

        # CNN
        n_mels = 128
        cnn_model, cnn_shape = cnn_net(n_mels)

        # BI-DIRECTIONAL RNN
        batch_size = 32
        bi_rnn = bi_directional_rnn(1024, batch_size=batch_size, output_dim=output_dim)

        # preprocessor
        sample_rate = 8000
        fft_size = 512
        frame_step = 256

        preprocessing_model = preprocess_model(
            sample_rate, fft_size, frame_step, n_mels
        )

        # build model
        cnn_bi_rnn_model = build_model(
            output_dim, cnn_model, bi_rnn, preprocessing_model
        )

        # load saved model
        cnn_bi_rnn_model.load_weights("../models/cnn-bi-rnn.h5")

    def validate_transcription(self , audiofile_path: list):
        transcriptions = []
        for f in audiofile_path:
            result = self.predict_transcription(f)
            transcriptions.push(result)
        return transcriptions


    def predict_transcription(self , filename):        
        samples, sample_rate = librosa.load('../data/tr_1_tr01001.wav' , sr=44100)

                # predict
        predicted, error = predict(
                    cnn_bi_rnn_model,
                    samples,
                    tokenizer,
                    int_to_char,
                    actual=None,
                )
                # build response
        return {"predicted": predicted , "error": error}
        # print()