import markovify
import re
import os
import random
import numpy as np
import codecs
import keras
import datetime
from keras.models import Sequential
from keras.layers import LSTM
from pronouncing_kr import rhymes, sorting_rhyme, nonefinding, make_rhymedict, make_schemedict, schemefinding

depth = 4
maxchars = 20
artist = "RAP"  # used when saving the trained model
rap_file = "neural_rap.txt"  # where the rap is written to

def create_network(depth):
    model = Sequential()
    model.add(LSTM(4, input_shape=(2, 2), return_sequences=True))
    for i in range(depth):
        model.add(LSTM(8, return_sequences=True))
    model.add(LSTM(2, return_sequences=True))
    model.summary()
    model.compile(optimizer='rmsprop',
                  loss='mse')

    return model


def markov(text_file):
    read = open(text_file, "r", encoding='utf-8').read()
    text_model = markovify.NewlineText(read)
    return text_model


def chars(line):
    count = 0
    line = line.replace(" ", "")
    line_parse = list(line)
    count += len(line_parse)
    if count == 0:
        count += 1
    return count / maxchars


def rhymeindex(lyrics):
    if str(artist) + ".rhymes" in os.listdir(".") :
        print("이전에 생성된 라임리스트( " + str(artist) + ".rhymes )를 불러오는 중..")
        return open(str(artist) + ".rhymes", "r", encoding="utf-8").read().split("\n")
    else:
        rhyme_master_list = []
        rhyme_dict = {}
        scheme_dict = {}
        print("라임리스트 생성중... ")
        for i in lyrics:
            word = re.sub(r"\W+", '', i.split(" ")[-1])
            if word in rhyme_dict:
                continue
            rhymeslist = rhymes(word)
            rhyme_dict[word] = rhymeslist
            rhymeslistends = []
            for i in rhymeslist:
                rhymeslistends.append(i[-2:])
            try:
                rhymescheme = max(set(rhymeslistends), key=rhymeslistends.count)
            except Exception:
                rhymescheme = word[-2:]
            rhyme_master_list.append(rhymescheme)
            scheme_dict[word[-2:]]=rhymescheme
        print("라임단어사전 생성..")
        make_rhymedict(rhyme_dict)
        print("완료!!")
        print("라임요소사전 생성..")
        make_schemedict(scheme_dict)
        print("완료!!")
        rhyme_master_list = list(set(rhyme_master_list))
        rhymelist = sorting_rhyme(rhyme_master_list)
        print("라임리스트 생성 완료!!! ")
        f = open(str(artist) + ".rhymes", "w", encoding='utf-8')
        f.write("\n".join(rhymelist))
        f.close()
        return rhymelist

def rhyme(line, rhyme_list):
    word = re.sub(r"\W+", '', line.split(" ")[-1])
    rhymescheme = schemefinding(word[-2:])
    try:
        float_rhyme = rhyme_list.index(rhymescheme)
    except Exception:  # 라임리스트에서 못찾으면
        print("nonefinding 중 ... ")
        float_rhyme = nonefinding(rhymescheme, rhyme_list)
    float_rhyme = float_rhyme / float(len(rhyme_list))
    return float_rhyme

def split_lyrics_file(text_file):
    text = open(text_file, "r", encoding='utf-8').read()
    text = text.split("\n")
    while "" in text:
        text.remove("")
    return text


def generate_lyrics(text_model, text_file):
    bars = []
    last_words = []
    lyriclength = len(open(text_file, "r", encoding='utf-8').read().split("\n"))
    markov_model = markov(text_file)
    print("len(bars) <", lyriclength / 9)
    while len(bars) < lyriclength / 9:
        bar = markov_model.make_sentence()
        print(bar)
        if type(bar) != type(None):
            print(chars(bar))
        if type(bar) != type(None) and chars(bar) < 1:

            def get_last_word(bar):
                last_word = bar.split(" ")[-1]
                if last_word[-1] in "!.?,":
                    last_word = last_word[:-1]
                return last_word

            last_word = get_last_word(bar)
            if bar not in bars and last_words.count(last_word) < 3:
                bars.append(bar)
                last_words.append(last_word)
        print("====> len(bars) : ", len(bars))
    print("원본 가사 개수 : ", lyriclength)
    print("markov로 만든 문장 개수 : ", len(bars))
    print("bars = ", bars)
    print("last_words = ", last_words)
    return bars


def build_dataset(lines, rhyme_list):
    dataset = []
    line_list = []
    for line in lines:
        line_list = [line, chars(line), rhyme(line, rhyme_list)]
        dataset.append(line_list)

    x_data = []
    y_data = []

    for i in range(len(dataset) - 3):
        line1 = dataset[i][1:]
        line2 = dataset[i + 1][1:]
        line3 = dataset[i + 2][1:]
        line4 = dataset[i + 3][1:]

        x = [line1[0], line1[1], line2[0], line2[1]]
        x = np.array(x)
        x = x.reshape(2, 2)
        x_data.append(x)

        y = [line3[0], line3[1], line4[0], line4[1]]
        y = np.array(y)
        y = y.reshape(2, 2)
        y_data.append(y)

    x_data = np.array(x_data)
    y_data = np.array(y_data)

    print("x shape " + str(x_data.shape))
    print("y shape " + str(y_data.shape))
    print("x_data = ", x_data, " / y_data = ", y_data)
    return x_data, y_data


def compose_rap(lines, rhyme_list, lyrics_file, model):
    rap_vectors = []
    human_lyrics = split_lyrics_file(lyrics_file)
    f = open(rap_file, "a", encoding='utf-8')
    initial_index = random.choice(range(len(human_lyrics) - 1))
    initial_lines = human_lyrics[initial_index:initial_index + 2]

    starting_input = []

    for line in initial_lines:
        print("원본 가사 : ", line)
        f.write("원본 가사:" + line + "\n")
        starting_input.append([chars(line), rhyme(line, rhyme_list)])
    print("starting_input")
    print(starting_input)

    starting_vectors = model.predict(np.array([starting_input]).flatten().reshape(1, 2, 2))
    rap_vectors.append(starting_vectors)

    for i in range(20):
        rap_vectors.append(model.predict(np.array([rap_vectors[-1]]).flatten().reshape(1, 2, 2)))
    return rap_vectors


def vectors_into_song(vectors, generated_lyrics, rhyme_list):
    print("\n\n")
    print(" 랩 가사 쓰는 중 (this could take a moment)...")
    print("\n\n")
    print("vectors")
    print(vectors)

    def last_word_compare(rap, line2):
        penalty = 0
        for line1 in rap:
            word1 = line1.split(" ")[-1]
            word2 = line2.split(" ")[-1]

            while word1[-1] in "?!,. ":
                word1 = word1[:-1]

            while word2[-1] in "?!,. ":
                word2 = word2[:-1]

            if word1 == word2:
                penalty += 0.2

        return penalty

    def calculate_score(vector_half, chars, rhyme, penalty):
        print(vector_half)
        desired_chars = vector_half[0]
        desired_rhyme = vector_half[1]
        desired_chars = desired_chars * maxchars
        desired_rhyme = desired_rhyme * len(rhyme_list)

        score = 1.0 - (
                    abs((float(desired_chars) - float(chars))) + abs((float(desired_rhyme) - float(rhyme)))) - penalty
        return score

    dataset = []
    for line in generated_lyrics:
        line_list = [line, chars(line), rhyme(line, rhyme_list)]
        dataset.append(line_list)
    rap = []

    vector_halves = []

    for vector in vectors:
        vector_halves.append(list(vector[0][0]))
        vector_halves.append(list(vector[0][1]))

    for vector in vector_halves:
        scorelist = []
        for item in dataset:
            line = item[0]
            print(item[0])
            if len(rap) != 0:
                penalty = last_word_compare(rap, line)
            else:
                penalty = 0
            print("vector, item[1], item[2], penalty")
            print(vector, item[1], item[2], penalty)
            total_score = calculate_score(vector, item[1], item[2], penalty)
            score_entry = [line, total_score]
            scorelist.append(score_entry)

        fixed_score_list = []
        for score in scorelist:
            fixed_score_list.append(float(score[1]))
        max_score = max(fixed_score_list)
        for item in scorelist:
            if item[1] == max_score:
                rap.append(item[0])
                print(str(item[0]))

                for i in dataset:
                    if item[0] == i[0]:
                        dataset.remove(i)
                        break
                break
    return rap


def train(x_data, y_data, model):
    model.fit(np.array(x_data), np.array(y_data),
              batch_size=2,
              epochs=5,
              verbose=1)
    model.save_weights(artist + ".rap")


def main(depth):
    startT = datetime.datetime.now()
    print("학습 시작... ( " + str(startT) + " )")

    model = create_network(depth)
    text_file = "lyrics.txt"

    bars = split_lyrics_file(text_file)

    st = datetime.datetime.now()
    print("라임 사전 구축중... ( " + str(st) + " )")

    rhyme_list = rhymeindex(bars)

    et = datetime.datetime.now()
    print("라임 사전 구축완료! ( " + str(et) + " )")
    print("===> 총 걸린 시간 : " + str(et - st))

    x_data, y_data = build_dataset(bars, rhyme_list)
    train(x_data, y_data, model)
    endT = datetime.datetime.now()
    print("학습 완료! ( " + str(endT) + " )")
    print("===> 총 걸린 시간 : " + str(endT - startT))


main(depth)
