import codecs
import re
import datetime
from pronouncing_kr import sorting_rhyme

# 유니코드 한글 시작 : 44032, 끝 : 55199
BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28

# 초성 리스트. 00 ~ 18
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# 중성 리스트. 00 ~ 20
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']

# 종성 리스트. 00 ~ 27 + 1(1개 없음)
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def make_dict() :
    start = datetime.datetime.now()
    print("사전 만드는 중... ( "+str(start)+" )")
    input_file = "lyrics.txt"
    output_file = "korean.dict"
    fp = codecs.open(input_file, 'r', encoding='utf-8')
    wp = codecs.open(output_file,"w",encoding='utf-8')
    text = fp.read()
    text = text.replace('\ufeff','')
    text = text.strip()
    lines = text.split("\n")
    word_list = []

    while "\r" in lines:
        lines.remove("\r")

    for line in lines:
        line = line.replace(' \r','')
        line = line.replace('.','')
        line = line.replace(',', '')
        line = line.replace('?', '')
        line = line.replace('!','')
        line = line.replace('~', '')
        # => 한문장으로는 안되는지...
        inputs = line.split(" ")

        for input in inputs:
            if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', input[:1]) is None:
                continue

            charac = ()
            test_keyword = input
            split_keyword_list = list(test_keyword)
            #print(split_keyword_list)

            cha = []

            for keyword in split_keyword_list:
                print(keyword)
                # 한글 여부 check 후 분리
                if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', keyword) is not None:
                    char_code = ord(keyword) - BASE_CODE
                    char1 = int(char_code / CHOSUNG)
                    char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
                    char3 = int((char_code - (CHOSUNG * char1) - (JUNGSUNG * char2)))

                    if JONGSUNG_LIST[char3] == ' ':
                        cha.append(CHOSUNG_LIST[char1] + JUNGSUNG_LIST[char2] + "P")
                    else:
                        cha.append(CHOSUNG_LIST[char1]+JUNGSUNG_LIST[char2]+JONGSUNG_LIST[char3])
            input = input.replace(" ","")
            input = input.replace("\r", "")
            input = input+" "+" ".join(cha)

            word_list.append(input)
            ## 중복된 값 없애기

    word_list = set(word_list)
    word_list = tuple(word_list)
    word_list = list(word_list)

    wp.write("\n".join(word_list))
    fp.close()
    wp.close()
    end = datetime.datetime.now()
    print("사전 구축 완료 ( " + str(end) + " )")
    print("===> 총 걸린 시간 : "+str(end-start))

def main():
    make_dict()

main()