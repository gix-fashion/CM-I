import re
import requests
import bs4
import os
import json


print("任务开始")
print("获取药材目录")
html = requests.get('http://zhongyaocai360.com/all.html')
html.encoding = 'gb18030'
html = html.text
soup = bs4.BeautifulSoup(html, 'html.parser')


all_list = soup.find('ul', class_='uzyc').find_all('li')
print("目录获取成功")
print("开始爬取")

flog_nonetype = open("log_nonetype.txt", "w", encoding='gb18030')
flog_unicode = open("log_unicode.txt", "w", encoding='gb18030')
flog_else = open("log_else.txt", "w", encoding='gb18030')

num = 0
total = 0

r = re.compile(r'[【](.*?)[】]')

for yaocai in all_list:
	yaocai_name = yaocai.find('a').text
	total = total + 1


	#if yaocai_name == "艾醋汤":#调试部分
	#	break
	if yaocai_name == "癌症":#第一个症状，之前全是方剂
		break

	if os.path.isfile("./yaocai/" + yaocai_name + ".json"):
		print("No." + str(total) + ": " + yaocai_name + " already exits")
		continue
	yaocai_url = yaocai.find('a').attrs['href']

	def getdetail(num, name, url):
		print("No." + str(total) +": grabbing " + yaocai_name + " from " + url)
		num = num + 1
		if num % 50 == 0:
			print("*****************************")
			print("本次已累计爬取" + str(num) + "种药方")
			print("*****************************")
		detail_html = requests.get(url, timeout=10)		
		detail_html.encoding = 'gb18030'
		return num, detail_html.text

	num, detail = getdetail(num, yaocai_name, yaocai_url)
	if detail is None:
		print("发生错误，跳出")
		continue
	
	detail_soup = bs4.BeautifulSoup(detail, 'html.parser')
	try:
		contentlist = detail_soup.find('div', class_='spider').find_all('p')
		data = {'药材名称': yaocai_name,
				'url': yaocai_url,}
		temptitle = None#有一些描述没有标题，用于将这样的描述添加到上一描述
		for content in contentlist:
			#print(content.text)
			if re.match(r, content.text) is not None:
				title = re.match(r, content.text).group()
				description = re.sub(u"【.*?】", "", content.text)
				data[title] = description
				temptitle = title
			else:
				description = re.sub(u"【.*?】", "", content.text)
				data[temptitle] = data[temptitle] + "    " +description#同一描述的两行之间用4个空格分开
	except AttributeError:
		flog_nonetype.write(yaocai_name + "%" + yaocai_url + '\n')
		continue
	except UnicodeEncodeError:
		flog_unicode.write(yaocai_name + "%" + yaocai_url + '\n')
		continue
	else:

		try:
			tempfile = open("./yaocai/" + yaocai_name + ".json", "w", encoding='gb18030')
			json.dump(data, tempfile, ensure_ascii=False, indent=4, separators=(',', ': '))
		except UnicodeEncodeError:
			flog_unicode.write(yaocai_name + "%" + yaocai_url + '\n')
			tempfile.close()
		except IOError:
			flog_else.write(yaocai_name + "%" + yaocai_url + "%" + "ioerror" + '\n')
		else:
			tempfile.close()

	
print("任务完成")

flog_else.close()
flog_unicode.close()
flog_nonetype.close()