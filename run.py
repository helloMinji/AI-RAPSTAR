import markovify
import re
import random
import numpy as np
import os
import codecs
import keras
import datetime
from keras.models import Sequential
from keras.layers import LSTM
from pronouncing_kr import rhymes, sorting_rhyme, nonefinding, fast_rhymeschemefinding


depth = 4
maxchars = 20
artist = "RAP" # used when saving the trained model
rap_file = "neural_rap.txt" # where the rap is written to

random_mode = False
my_index = 16358

def create_network(depth):
	model = Sequential()
	model.add(LSTM(4, input_shape=(2, 2), return_sequences=True))
	for i in range(depth):
		model.add(LSTM(8, return_sequences=True))
	model.add(LSTM(2, return_sequences=True))
	model.summary()
	model.compile(optimizer='rmsprop',
              loss='mse')

	if artist + ".rap" in os.listdir(".") :
		model.load_weights(str(artist + ".rap"))
		print ("이전에 학습시킨 모델 불러오는 중.. : " + str(artist) + ".rap")
	return model

def markov(text_file):
	read = open(text_file, "r",encoding='utf-8').read()
	text_model = markovify.NewlineText(read)
	return text_model

def chars(line):
	count = 0
	line = line.replace(" ","")
	line_parse = list(line)
	count += len(line_parse)
	if count == 0:
		count +=1
	return count / maxchars

def rhymeindex(lyrics):
	if str(artist) + ".rhymes" in os.listdir("."):
		print ("이전에 생성한 라임리스트 불러오는 중.. : " + str(artist) + ".rhymes" )
		return open(str(artist) + ".rhymes", "r", encoding="utf-8").read().split("\n")
	else:
		rhyme_master_list = []
		print ("Alright, building the list of all the rhymes" )
		for i in lyrics:
			word = re.sub(r"\W+", '', i.split(" ")[-1]).lower()
			rhymeslist = rhymes(word)
			rhymeslistends = []
			for i in rhymeslist:
				rhymeslistends.append(i[-2:])
			try:
				rhymescheme = max(set(rhymeslistends), key=rhymeslistends.count)
			except Exception:
				rhymescheme = word[-2:]
			print("===> rhymescheme : ",rhymescheme)
			rhyme_master_list.append(rhymescheme)
		rhyme_master_list = list(set(rhyme_master_list))
		rhymelist = sorting_rhyme(rhyme_master_list)

		f = open(str(artist) + ".rhymes", "w",encoding='utf-8')
		f.write("\n".join(rhymelist))
		f.close()
		print (rhymelist)
		return rhymelist

def rhyme(line, rhyme_list):
	word = re.sub(r"\W+", '', line.split(" ")[-1])
	rhymescheme=fast_rhymeschemefinding(word)
	if rhymescheme is None:
		rhymescheme = word[-2:]
	try:
		float_rhyme = rhyme_list.index(rhymescheme)
	except Exception: #라임리스트에서 못찾으면
		float_rhyme = nonefinding(rhymescheme,rhyme_list)
	float_rhyme = float_rhyme / float(len(rhyme_list))
	return float_rhyme

def split_lyrics_file(text_file):
	text = open(text_file,"r",encoding='utf-8').read()
	text = text.split("\n")
	while "" in text:
		text.remove("")
	return text


def generate_lyrics(text_file):
	print("markov로 문장 생성중... ")
	bars = []
	last_words = []
	lyriclength = len(open(text_file,"r",encoding='utf-8').read().split("\n"))
	print("원본가사로 markov모델 생성..")
	markov_model = markov(text_file)
	print(".. 완료!!")

	# lyriclength / 9 값을 증가시켜서 더많이 생성시킬 수 있음!
	print("markov모델을 이용해 ",lyriclength / 9, "개의 문장을 생성합니다.")
	while len(bars) < lyriclength / 9 :
		bar = markov_model.make_sentence()
		print(bar)
		if type(bar) != type(None):
			pass
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
		print("====> 현재 수집된 문장 개수 : ",len(bars))
	print("markov로 새로운 문장생성 완료!! ( 원본 가사 개수 : ",lyriclength," | markov로 만든 문장 개수 : ",len(bars)," )")
	print("만들어진 문장")
	print(bars)
	return bars
	
def compose_rap(rhyme_list, lyrics_file, model):
	print("훈련된 LSTM모델을 이용한 예측시작..")
	rap_vectors = []
	human_lyrics = split_lyrics_file(lyrics_file)
	f = open(rap_file, "a", encoding='utf-8')
	fv = open("vector_info.txt", "a", encoding='utf-8')

	if random_mode is True:
		print("원본 가사에서 랜덤한 2문장 고르는 중!")
		initial_index = random.choice(range(len(human_lyrics) - 1))
	else:
		initial_index = my_index
	initial_lines = human_lyrics[initial_index:initial_index + 2]
	
	starting_input = []

	print("고른 가사 ↓")
	for line in initial_lines:
		print(line)
		f.write("원본 가사:"+line+"\n")
		starting_input.append([chars(line), rhyme(line, rhyme_list)])
	print("가사문장 벡터화 ↓")
	print(starting_input)
	fv.write("starting_input:\n")
	for v in starting_input:
		fv.write(str(v)+"\n")

	starting_vectors = model.predict(np.array([starting_input]).flatten().reshape(1, 2, 2))
	rap_vectors.append(starting_vectors)

	print("20개의 예측 벡터값 생성..")
	for i in range(20):
		rap_vectors.append(model.predict(np.array([rap_vectors[-1]]).flatten().reshape(1, 2, 2)))
	print("..완료!! ↓")
	print(rap_vectors)

	fv.write("rap_vectors:\n")
	for v in rap_vectors:
		fv.write(str(v)+"\n")

	return rap_vectors
	
def vectors_into_song(vectors, generated_lyrics, rhyme_list):
	print ("\n\n")
	print ("이제 LSTM모델의 예측데이터로 markov문장을 선별합니다.")
	print ("\n\n")
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

		score = 1.0 - (abs((float(desired_chars) - float(chars))) + abs((float(desired_rhyme) - float(rhyme)))) - penalty
		return score

	print("먼저 markov로 생성된 가사를 숫자데이터로 바꾸는 중... ")
	dataset = []
	for line in generated_lyrics:
		line_list = [line, chars(line), rhyme(line, rhyme_list)]
		print(line_list)
		dataset.append(line_list)
	rap = []
	print(".. 완료!!")
	vector_halves = []
	
	for vector in vectors:
		vector_halves.append(list(vector[0][0])) 
		vector_halves.append(list(vector[0][1]))

	print("LSTM 예측값과 markov문장의 숫자값을 비교하여 선별점수계산 중..")
	print(" ( 최고점수는 1.0 점으로 점수가 가장 높은 문장을 선별합니다. )")
	for vector in vector_halves:
		print("vector값 : ",vector)
		scorelist = []

		for item in dataset:
			line = item[0]
			if len(rap) != 0:
				penalty = last_word_compare(rap, line)
			else:
				penalty = 0
			total_score = calculate_score(vector, item[1], item[2], penalty)
			score_entry = [line, total_score]
			print(score_entry)
			scorelist.append(score_entry)
		
		fixed_score_list = []
		for score in scorelist:
			fixed_score_list.append(float(score[1]))
		max_score = max(fixed_score_list)
		print("최고점 : ",max_score)
		for item in scorelist:
			if item[1] == max_score:
				rap.append(item[0])
				print (str(item[0]) ," ** 선별 **")
				
				for i in dataset:
					if item[0] == i[0]:
						dataset.remove(i)
						break
				break
	return rap

def main(depth):
	startR = datetime.datetime.now()
	print("생성 시작... ( " + str(startR) + " )")

	model = create_network(depth)
	text_file = "lyrics.txt"

	bars = generate_lyrics(text_file)

	sr = datetime.datetime.now()
	print("생성한 문장의 라임 분석 중.. ( " + str(sr) + " )")

	rhyme_list = rhymeindex(bars)

	er = datetime.datetime.now()
	print("라임 분석 완료! ( " + str(er) + " )")
	print("===> 총 걸린 시간 : " + str(er - sr))

	vectors = compose_rap(rhyme_list, text_file, model)
	rap = vectors_into_song(vectors, bars, rhyme_list)
	f = open(rap_file, "a",encoding='utf-8')
	print("완성된 랩 가사")
	for bar in rap:
		print(bar)
		f.write(bar)
		f.write("\n")
	endR = datetime.datetime.now()
	print("랩가사 작사 끝! ( " + str(endR) + " )")
	print("===> 총 걸린 시간 : " + str(endR - startR))
		
main(depth)
