'''
LTP汉语自然语言处理原理与实践
'''

from pyltp import *  #导入ltp库


MODEL_PATH = "/home/leo/NLP/Model_Library/ltp3.4/cws.model" #ltp3.4 分词模型库
USER_DICT = "/home/leo/NLP/Model_Library/ltp3.4/fulluserdict.txt"
#外部用户自定义词典

segmentor = Segmentor() #实例化分词模块


segmentor.load(MODEL_PATH) #加载分词库
words = segmentor.segment("我家住在上地东路35号颐泉汇C座338房间。")
print("|".join(words)) #分割后的分词结果


segmentor = Segmentor() #实例化分词模块
segmentor.load_with_lexicon(MODEL_PATH, USER_DICT) #加载专有名词词典
sent = "我家住在上地东路35号颐泉汇C座338房间。"
seg_result = segmentor.segment(sent)
seg_result = "|".join(seg_result)
seg_result = seg_result.replace("|"," ")

words = seg_result.split(" ")
postagger = Postagger() #实例化词性标注类
postagger.load("/home/leo/NLP/Model_Library/ltp3.4/pos.model")
postags = postagger.postag(words)

recognizer = NamedEntityRecognizer()
recognizer.load("/home/leo/NLP/Model_Library/ltp3.4/ner.model")
netags = recognizer.recognize(words, postags)


for word, postag, netag in zip(words, postags, netags):
    print(word + "/" + postag + "/" + netag)

