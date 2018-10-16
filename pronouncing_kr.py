import codecs
import re
import collections
import pkg_resources
import random

KOR_DICT = './korean.dict'

pronunciations = None
lookup = None
rhyme_lookup = None

def _stream(resource_name):
    stream = pkg_resources.resource_stream(__name__, resource_name)
    return stream

def dict_stream():
    stream = _stream(KOR_DICT)
    return stream

def parse_kordict(korhd):
    pronunciations = list()
    for line in korhd:
        line = line.strip().decode('utf-8')
        line = line.replace('\ufeff', '')
        word, phones = line.split(" ", 1)
        pronunciations.append((word, phones))
    return pronunciations

def init_kodict(filehandle=None):
    global pronunciations, lookup
    if pronunciations is None:
        if filehandle is None:
            filehandle = dict_stream()
        pronunciations = parse_kordict(filehandle)
        filehandle.close()
        lookup = collections.defaultdict(list)
        for word, parses in pronunciations:
            if lookup.get(word) is None:
                lookup[word].append(parses)

def sorting_rhyme(rhyme_list):
    parse_word = collections.defaultdict(list)
    for line in rhyme_list:
        parses = parses_for_word(line)
        parse = parses.replace(" ",'')
        reverse_chars = parse[::-1]
        parse_word[line].append(reverse_chars)

    sorting_word = sorted(parse_word.items(), key=lambda t: t[1])
    print(sorting_word)

    result = []
    for line in sorting_word:
        result.append(line[0].replace('\r', ''))

    return result

def rhymes(word):
    init_kodict()
    parse = parses_for_word(word)
    rhyme_point = collections.defaultdict(list)
    for word, parses in pronunciations:
        point = calculate_point(parse,parses)
        rhyme_point[word].append(point)
    rhyme_word = sorted(rhyme_point.items(),key= lambda t:t[1] ,reverse = True)
    rhymes = []
    for tuple in rhyme_word:
        if tuple[1][0] > 80 and tuple[1][0] != 100 :
            rhymes.append(tuple[0])
    return rhymes

def nonefinding(rhymescheme,rhyme_list):
    parse_sch = parses_for_word(rhymescheme)
    score = []
    for word in rhyme_list:
        parses = parses_for_word(word)
        point = calculate_point(parse_sch,parses)
        score.append(point)
    selections = []
    for i in score:
        num = score.index(i)
        if i == max(score):
            selections.append(rhyme_list[num])
            score[num]=0
    select = random.choice(selections)
    float_rhyme = rhyme_list.index(select)
    return float_rhyme


    # parse 가 기준 단어
    # parses는 dictionary에 있는 단어
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

def parses_for_word(word) :
    BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28

    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ',
                         'ㅢ', 'ㅣ']
        # 비슷한 중성 모음 만들기!!!
    JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ',
                         'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    split_word = list(word)

    cha = []

    for split in split_word:
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', split) is not None:
            char_code = ord(split) - BASE_CODE
            char1 = int(char_code / CHOSUNG)
            char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
            char3 = int((char_code - (CHOSUNG * char1) - (JUNGSUNG * char2)))

            if JONGSUNG_LIST[char3] == ' ':
                cha.append(CHOSUNG_LIST[char1] + JUNGSUNG_LIST[char2] + "P")
            else:
                if char1 < 0 or char2 < 0 or char3 < 0 :
                    continue
                cha.append(CHOSUNG_LIST[char1] + JUNGSUNG_LIST[char2] + JONGSUNG_LIST[char3])

    parse_word = " ".join(cha)

    return parse_word

