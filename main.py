import argparse

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--words', type=str, default='')
parser.add_argument('--org', type=str, default='')
parser.add_argument('--ans', type=str, default='')
args = parser.parse_args()

'''
if __name__ == '__main__':
    print(args.words)
    print(args.org)
    print(args.ans)
    # 命令行输入这个
    # python cmd_parameter.py --string=python --int-input=10 --list-input=123
'''
global Total
Total = 0

class Solution:
    # 获取next数组
    def get_next(self, T):
        i = 0
        j = -1
        next_val = [-1] * len(T)
        while i < len(T)-1:
            if j == -1 or T[i] == T[j]:
                i += 1
                j += 1
                # next_val[i] = j
                if i < len(T) and T[i] != T[j]:
                    next_val[i] = j
                else:
                    next_val[i] = next_val[j]
            else:
                j = next_val[j]
        return next_val

    # KMP算法
    def kmp(self, S, T):
        i = 0
        j = 0
        next = self.get_next(T)
        while i < len(S) and j < len(T):
            if j == -1 or S[i] == T[j]:
                i += 1
                j += 1
            else:
                j = next[j]
        if j == len(T):
            return i - j
        else:
            return -1


def sensitiveFinder(sentence_list, file):
    global Total
    s = Solution()
    f = open("words.txt", "r", encoding='utf-8')
    readRes = f.read()
    sensitiveWords = readRes.split('\n')
    #print("len of sensitiveWords============", len(sensitiveWords))
    print(sensitiveWords)
    for line, sentence in enumerate(sentence_list):
        for word in sensitiveWords:
            i = 0
            a = sentence.find(word)
            while a != -1:
                Total += 1
                str_word = "Line" + str(line) + ": <" + word + "> " + word + "\n"
                file.write(str_word)
                #print("line:%d %s", line+1, word)
                a = sentence.find(word, a+1)

    print(Total)


if __name__ == '__main__':
    fo = open("org.txt", "r", encoding='utf-8')
    fa = open("ans1.txt", "w", encoding='utf-8')
    o = fo.readlines()
    sensitiveFinder(o, fa)
