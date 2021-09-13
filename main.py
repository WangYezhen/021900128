import argparse
from pypinyin import lazy_pinyin
from pychai import Schema
import re
import time

# 定义参数
parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--words', type=str, default='')
parser.add_argument('--org', type=str, default='')
parser.add_argument('--ans', type=str, default='')
args = parser.parse_args()

'''
    # 命令行输入这个
    # python main.py --words=路径 --org=路径 --ans=路径
'''
global Total
Total = 0


def initChaizi():
    wubi98 = Schema('wubi98')
    wubi98.run()
    for nameChar in wubi98.charList:
        if nameChar in wubi98.component:
            scheme = wubi98.component[nameChar]
        else:
            tree = wubi98.tree[nameChar]
            componentList = tree.flatten_with_complex(wubi98.complexRootList)
            scheme = sum((wubi98.component[component] for component in componentList), tuple())
        if len(scheme) == 1:
            objectRoot = scheme[0]
            nameRoot = objectRoot.name
            # 单根字中的键名字，击四次该键，等效于取四次该字根
            if nameChar in '王土大木工目日口田山禾白月人金言立水火之已子女又幺':
                info = [nameRoot] * 4
            # 单根字中的单笔画字，取码为双击该键加上两个 L
            elif nameChar in '一丨丿丶乙':
                info = [nameRoot] * 2 + ['田'] * 2
            # 普通字根字，报户口 + 一二末笔
            else:
                firstStroke = objectRoot.strokeList[0].type
                secondStroke = objectRoot.strokeList[1].type
                if objectRoot.charlen == 2:
                    info = [nameRoot, firstStroke, secondStroke]
                else:
                    lastStroke = objectRoot.strokeList[-1].type
                    info = [nameRoot, firstStroke, secondStroke, lastStroke]
        elif len(scheme) < 4:
            if nameChar in wubi98.component or tree.structure not in 'hz':
                weima = '3'
            elif tree.structure == 'h':
                weima = '1'
            elif tree.structure == 'z':
                weima = '2'
            lastObjectRoot = scheme[-1]
            quma = wubi98.category[lastObjectRoot.strokeList[-1].type]
            shibiema = quma + weima
            info = [objectRoot.name for objectRoot in scheme] + [shibiema]
        elif len(scheme) > 4:
            scheme = scheme[:3] + scheme[-1:]
            info = [objectRoot.name for objectRoot in scheme]
        else:
            info = [objectRoot.name for objectRoot in scheme]
        code = ''.join(wubi98.rootSet[nameRoot] for nameRoot in info)
        wubi98.encoder[nameChar] = code
    return wubi98


def createChaizi(chai, word):
    if word == '\n' or ('a' <= word <= 'z') or ('A' < word < 'Z') or word.isdigit():
        return '0'
    if word in chai.tree.keys():
        return chai.tree[word].first.name[0], chai.tree[word].second.name[0]
    else:
        return '0'


def sensitiveFinder(sentence_list, regular_list, regular_chai_list,pinyin_list, sensitiveWords):
    global Total
    for line, sentence in enumerate(sentence_list):# 一行一行检测
        for num, regular in enumerate(regular_chai_list):
            for i in re.finditer(regular, sentence, re.I):
                ans = 'Line' + str(line+1) + ':' + ' <' + sensitiveWords[num] + '> ' + i.group()
                print(ans)
                Total += 1

        location = []
        for loc, word in enumerate(sentence):
            for pinyin in pinyin_list:
                if ''.join(lazy_pinyin(word)) == pinyin[1] and word != pinyin[0]:
                    location.append((loc, word))
                    s1 = list(sentence)
                    s1[loc] = pinyin[0]
                    sentence = ''.join(s1)
        for num, regular in enumerate(regular_list):
            for i in re.finditer(regular, sentence, re.I):
                flag = 1
                for duoyinzi in location:
                    if i.span()[0] <= duoyinzi[0] <= i.span()[1]:
                        s2 = list(sentence)
                        s2[duoyinzi[0]] = duoyinzi[1]
                        sentence = ''.join(s2)
                        flag = 0
                if flag == 1:
                    ans = 'Line' + str(line+1) + ':' + ' <' + sensitiveWords[num] + '> ' + i.group()
                else:
                    ans = 'Line' + str(line + 1) + ':' + ' <' + sensitiveWords[num] + '> ' + sentence[i.span()[0]:i.span()[1]]
                print(ans)
                Total += 1
    print(Total)


def creatRegular(dict_word, flag):
    regular = []
    if flag == 1:
        for key in dict_word: # 键值
            length_key = len(key)
            regular_key = ''
            regular_key_chai = ''
            for num, character in enumerate(key): # 每个字
                if 'a' <= character[0] <= 'z' or 'A' <= character[0] <= 'Z': # 英文单词
                    if num+1 == length_key:
                        regular_key += '(?:' + character + '|' + character.upper() + ')'
                    else:
                        regular_key += '(?:' + character + '|' + character.upper() + ')[^\\u4e00-\\u9fa5]*'

                else: # 中文汉字
                    pinyin = ''.join(lazy_pinyin(character))
                    if num+1 == length_key:
                        regular_key += '(?:' + pinyin + '|' + pinyin[
                            0] + '|' + character + ')'
                    else:
                        regular_key += '(?:'+pinyin+'|'+pinyin[0]+'|'+character+')[^\\u4e00-\\u9fa5]*'
            regular.append(regular_key)

    else:
        for key in dict_word:  # 键值
            length_key = len(key)
            regular_key = ''
            for num, character in enumerate(key):  # 每个字
                if 'a' <= character[0] <= 'z' or 'A' <= character[0] <= 'Z':  # 英文单词
                    continue
                else:  # 中文汉字
                    character_chai = ''
                    for pianpang in dict_word[key][num]:
                        if pianpang == '0':
                            continue
                        else:
                            character_chai += pianpang
                    if num + 1 == length_key:
                        regular_key += '(?:' + character_chai + ')'
                    else:
                        regular_key += '(?:' + character_chai + ')[^\\u4e00-\\u9fa5]*'
            if regular_key != '':
                regular.append(regular_key)

    print(regular)
    return regular


if __name__ == '__main__':
    start=time.time()
    file_word = open("words.txt", 'r', encoding='utf-8')
    file_org = open("org.txt", 'r', encoding='utf-8')
    text = file_org.readlines()
    readRes = file_word.read()
    sensitiveWords = readRes.split('\n')

    pinyin_list = []
    for word in sensitiveWords:
        pinyin_word_list = []
        for character in word:
            if 'a' <= character <= 'z' or 'A' <= character <= 'Z':
                break
            else:
                pinyin_list.append((character, ''.join(lazy_pinyin(character))))

    dict_word = {}
    chai = initChaizi()
    for word in sensitiveWords:
        if 'a' <= word[0] <= 'z' or 'A' <= word[0] <= 'Z':
            dict_singleword = {word: None}
            dict_word.update(dict_singleword)
            continue
        chai_word_list = []
        for character in word:
            chai_word_list.append(createChaizi(chai, character))
        chai_word_tuple = tuple(chai_word_list)
        dict_singleword = {word: chai_word_tuple}
        dict_word.update(dict_singleword)
    #creatRegular(dict_word)
    sensitiveFinder(text, creatRegular(dict_word, 1), creatRegular(dict_word, 0), pinyin_list, sensitiveWords)
    end = time.time()
    print('Running time: %s Seconds'%(end-start))
