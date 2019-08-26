import jieba
import jieba.analyse
import xlwt
import os
import json


word_list = []
key_list = []
word_dict = {}
without_list = []
wf = open("WordCount.txt", 'w', encoding='gb18030')
wf_without = open("WordCount_withou.txt", 'w', encoding='gb18030')
num = 0

for root, dirs, files in os.walk('D:\\workspace\\spider\\化学专业数据库-中药\\中药复方\\yaocai'):
	for file in files:
		with open(('D:\\workspace\\spider\\化学专业数据库-中药\\中药复方\\yaocai\\' + file), 'r', encoding='gb18030') as f:
			text = json.load(f, encoding='gb18030')
			f.close()
			if '【性味】' not in text and '性味' not in text:
				without_list.append(text['药材名称'])
				continue

			print(text['药材名称'])
			if '【性味】' in text:
				zhuzhi = text['【性味】']
			elif '性味' in text:
				zhuzhi = text['性味']
			num += 1
			print("已统计文件数量：" + str(num))
			item = zhuzhi.strip('    ').split('\t')
			tags = jieba.analyse.extract_tags(item[0])
			for t in tags:
				word_list.append(t)


for item in word_list:
	if item not in word_dict:
		word_dict[item] = 1
	else:
		word_dict[item] +=1

orderList = list(word_dict.values())
orderList.sort(reverse=True)
for i in range(len(orderList)):
	for key in word_dict:
		if word_dict[key] == orderList[i]:
			wf.write(key + ' ' + str(word_dict[key]) + '\n')
			key_list.append(key)
			word_dict[key] = 0

for without in without_list:
	wf_without.write(without + '\n')

wbk = xlwt.Workbook(encoding = 'gb18030')
sheet = wbk.add_sheet('WordCount')
sheet_extra = wbk.add_sheet('without_zhuzhi')
for i in range(len(key_list)): 
	sheet.write(i, 1, label = orderList[i]) 
	sheet.write(i, 0, label = key_list[i]) 
wbk.save('wordCount.xls') #保存为 wordCount.xls文件

wf.close()
wf_without.close()
