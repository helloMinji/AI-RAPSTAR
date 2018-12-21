![image](https://user-images.githubusercontent.com/41939828/50338952-5b176980-0559-11e9-9b08-f9cd4a41ce53.png)

### > About "AI RAPSTAR"

> LSTM과 Markov Chain을 이용한 랩 생성 프로그램으로,  
> 프로그램에 래퍼의 가사를 이용하여 각 가사의 라임 형태와 전반적인 라임 흐름을 학습시켜  
> 적절한 문맥을 가진 랩을 생성하는 프로그램.  
>   
  - 기존에 이루어진 다수의 영어기반 프로젝트들과 달리 한글에 기반한 프로그램.
  - 기존 가사에 있는 단어들의 자모음을 분리하여 DB를 구축하고, 이를 기반으로 새로운 라임규칙을 만들어 적용한다.
  - 기존의 가사를 이용하여 다양한 조합을 통해 창의적인 가사를 생성한다.  


---------------------------------------------------------------

### > How to Use

####  Setup

리눅스 환경 + 아나콘다 이용
```linux
conda create --name rapping python=2 (가상환경 생성)
source activate rapping
cd rapping-neural-network-master/ (프로젝트 파일이 있는 위치)
pip install tensorflow
pip install keras (옵션)
pip install -U -r requirements.txt
python model.py
```


#### Train

- model.py 파일에서 lylics.txt를 원하는 가사로 변경 후 사용하십시오.
- model.py 파일에서 artist 변수의 값을 원하는 가수 이름으로 변경하십시오. - 이후 결과 파일을 생성할 때 해당 값이 이용됩니다.
- python model.py로 파일을 실행하되, train_mode 변수를 True로 지정하십시오.


#### Test

- python model.py로 파일을 실행하되, train_mode 변수를 False로 지정하십시오.
- 결과는 neural_rap.txt 파일에 저장됩니다.


#### Result

예시 결과 및 train, test 과정을 확인할 수 있습니다.
- Youtube : https://www.youtube.com/channel/UCguqCFyz7bv1hnPMslwH2VA
- SoundCloud : https://soundcloud.com/user-364733903



---------------------------------------------------------------

### > 동작 원리

#### 시스템 흐름도
![image](https://user-images.githubusercontent.com/41939828/50339083-ce20e000-0559-11e9-94ae-edca835ca3a1.png)

#### LSTM

LSTM은 이 프로그램에서 원본 가사에서 각 문장의 총 단어 수와 마지막 단어의 라임 요소를 추출합니다.  
그리고 이 데이터를 숫자 데이터 형태로 변환하여 모델을 훈련시켜 모델에 원본 가사의 문장 형식이 학습되도록 합니다.

#### Markov Chain

Markov Chain은 이 프로그램에서 확률에 따라 문장을 만들어내고, 기존 가사와 유사도가 70%가 넘지 않는 문장을 선별하는 역할을 합니다.

#### model.py
```python
def rhymeindex(lyrics):
	if str(artist) + ".rhymes" in os.listdir(".") and train_mode == False:
		print ("loading saved rhymes from " + str(artist) + ".rhymes" )
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
```

> model.py 내의 라임파일을 생성하는 모듈이다.  
> 한 문장 내의 단어를 기준으로 라임을 이루는 단어를 저장한다.
>
> 만약 디렉토리 안의 가수이름.rhymes 파일이 존재하며 트레이닝 모드가 아닐 때는 그 파일을 가사 생성에 이용한다.  
> 그렇지 않을 경우 라임 리스트를 생성한다.  
> ( rhymescheme : 문장의 맨 끝의 두글자 구조로 이루어짐 )  
> 
#### make_dict.py
```python
for keyword in split_keyword_list:
  print(keyword)
  
  if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', keyword) is not None:
    char_code = ord(keyword) - BASE_CODE
    char1 = int(char_code / CHOSUNG)
    char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
    char3 = int((char_code = (CHOSUNG * char1) - (JUNGSUNG * char2)))
    
    if JONGSUNG_LIST[char3] == ' ':
      cha.append(CHOSUNG_LISG[char1] + JUNGSUNG_LISG[char2] + "P")
    else:
      cha.append(CHOSUNG_LIST[char1] + JUNGSUNG_LIST[char2] + JONGSUNG_LIST[char3])
      
input = input.replace(" ","").replace("\r","")
input = input+" "+" ".join(cha)
```

> 한글 사전을 생성하는 모듈이다.  
> 학습데이터로 넣은 가사의 단어를 자모음 분리하여 한글자모사전을 생성한다.  

#### pronouncing_kr.py
```python
def calculate_point(parse,parses):
    point = 0 # 총 포인트

    plus = 5 # 가산점
    # 단어 내 문자갯수를 세기 위해서 쪼개는 부분
    parse_list = parse.split()
    parses_list = parses.split()

    length = len(parse_list)
    if len(parses_list) == len(parse_list):
        point += 10*3 # 길이 같으면 가산점
    else:
        if len(parses_list) > len(parse_list):
            #문자 갯수 차이클수록 점수 적음
            num = len(parses_list) - len(parse_list)
            if num < 3:
                point += 10*(3- num)

            length = len(parse_list)
            index = -(length*3+(length-1))
            parses = parses[index:]
        else:
            num = len(parse_list) - len(parses_list)
            if num < 3:
                point += 10 * (3 - num)

            length = len(parses_list)
            index = -(length * 3 + (length - 1))
            parse = parse[index:]

    parse_list = parse.split()
    parses_list = parses.split()
    for i in range(length - 1, -1, -1):
        c_point = 0  # 글자당 포인트
            # 초성
        if parses_list[i][0] == parse_list[i][0]:
            c_point +=1
            # 중성 ## 같은 발음나는 그룹 묶는 걸로 고쳐야함!!
        if parses_list[i][1] == parse_list[i][1]:
            c_point +=3
            # 종성
        if parses_list[i][2] == parse_list[i][2]:
            c_point +=2
        c_point*=plus # 가산점주기
        if plus != 1:
            plus-=1
        point+=c_point

    whole_point = 0
    for i in range(length):
        whole_point+=(5-i)*6
    whole_point+=30

    if point == 0 :
        point +=1
    return ( point / whole_point ) * 100
```

> 한글 사전을 활용하는 모듈이다.  
> 한글 자모사전에 있는 단어를 유사한 정도에 따라 가산점을 부여하고 총점을 계산한다.   

---------------------------------------------------------------

### > Developer
![image](https://user-images.githubusercontent.com/41939828/50339246-4c7d8200-055a-11e9-9aa9-982690123a60.png)


- 김지혜
- 홍민지 [@helloMinji](https://github.com/helloMinji)
- 김예림
- 임혜린

---------------------------------------------------------------

### > Open Library
* **영어 랩 작사 프로그램**
  > 링크: https://github.com/robbiebarrat/rapping-neural-network
  * 영어로 된 가사를 입력으로 제공하면 영어 랩을 작사하는 프로그램

* **초성, 중성, 종성 분리 알고리즘**
  > 링크: https://github.com/Jihoon-SHIN/JellyLab/tree/2e6da3a112ab0093164d8fd7bbb1cfe1b7db0b78/Korean_handle
  * 초성, 중성, 종성을 유니코드 값을 이용하여 분리하는 알고리즘
  
* **영어발음사전**
  > 링크: https://github.com/aparrish/pronouncingpy
  * 카네기 멜론 대학이 북미 영어를 위해 만든 공개 소프트웨어 발음 사전
  * 134,000개 이상의 단어와 발음이 포함되어 있음
  * 이를 참고하여 한글발음사전을 새로 생성함!
  
  

