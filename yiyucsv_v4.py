import requests
import re
import urllib.request, urllib.parse, urllib.error
import sys
import csv
import os
import time
import random
import collections
from bs4 import BeautifulSoup

'''
//*[@id="list"]/div[1]/div[2]/ul/li[1]/div[1]/p/a[2]
'''

nums = collections.OrderedDict()#暫存已存在的askyiyu.csv所有內容
if os.path.isfile('askyiyu.csv'): 	#若'askyiyu.csv'檔案 存在
	#讀取過去已寫入的資料'問題編號', '問題連結','提問人性別','提問人年齡','提問的標題','提問的內容','回覆數','醫生們的回覆'
	fr= open('askyiyu.csv','r', newline='',encoding='utf-8-sig')
	reader = csv.reader(fr)
	
	for row in reader:
		nums[row[0]]= row 	#用ordered dictionary暫存內容 key是提問編號 value是每一擇提問資料
	del nums['num']			#刪除標頭
	print('askyiyu.csv已存在，共',len(nums),'筆Q&A。')
	fr.close()
							
#'問題編號', '問題連結','提問人性別','提問人年齡','提問的標題','提問的內容','回覆數','醫生們的回覆'
csvheader = ['num','link','gender','age','title','question','num_ans','answers'] #CSV的標頭
f= open('askyiyu.csv','w', newline='',encoding='utf-8-sig')
f_csv = csv.writer(f)
f_csv.writerow(csvheader)

doctors = collections.OrderedDict() #暫存已存在的doctors.csv所有內容
if  os.path.isfile('doctors.csv'): #若'doctors.csv'檔案 存在
	#讀取過去已寫入的醫生資料 '問題編號', '問題連結','醫生','醫生個人資訊link'
	fr2= open('doctors.csv','r', newline='',encoding='utf-8-sig')
	reader2 = csv.reader(fr2)
	i=0
	for row2 in reader2:
		if row2[0] in doctors:
			doctors[row2[0]].update({i:row2})
		else:
			i=0
			doctors.update({row2[0]:{i:row2}})
		i+=1
		
	print('doctors.csv已存在')
	del doctors['num']	#刪除標頭	
	fr2.close()
	
#'問題編號', '問題連結','醫生','醫生個人資訊link'
csvheader2 = ['num','link','doctor','doc_info'] #CSV的標頭
f2= open('doctors.csv','w', newline='',encoding='utf-8-sig')
f2_csv = csv.writer(f2)
f2_csv.writerow(csvheader2)
	

total=0 #統計抓取份數
new_nums = [] #記錄這次執行所抓取的問題編號
def run(a,number):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Cookie': '__jsluid=751d12a60b57460bf5efd93a2314a4d5; Hm_lvt_7c2c4ab8a1436c0f67383fe9417819b7=1478143992; Hm_lpvt_7c2c4ab8a1436c0f67383fe9417819b7=1478144595; CNZZDATA30036369=cnzz_eid%3D909790220-1478143944-%26ntime%3D1478143944; TUSHENGSID=TS1478143994332',
        'Connection': 'close',
        'Upgrade-Insecure-Requests': '1'
    }

    r = requests.get("http://www.120ask.com/list/yiyu/all/"+str(a),headers = headers)
    soup = BeautifulSoup(r.text, "lxml")
    text = soup.find_all('div', class_='fl h-left-p')
	
    for i in text:

        title = i.find_all('a')
        link = title[0].get('href') #提問連結
        qnum =  link.replace('http://www.120ask.com/question/','')
        qnum =  qnum.replace('.htm','') # question_num
        #print(link, end=' ') #連結
		
        rl = requests.get(link,headers = headers) 
        ask = BeautifulSoup(rl.text, "lxml")
        ask_info = ask.find_all('div', class_='b_askti') #提問者的資訊: 標題、性別、歲數、提問時間、多少人回覆
        new_ask_info = ask_info[0].text.strip().split('\n') #將提問者的資訊以'\n'切割
		
		#抓取有多少醫生回覆
        fetchkey ='人回复'
        num_ans=''
        for l in new_ask_info:
           if fetchkey in l:
              num_ans = l	#多少醫生回覆
        num_ans = num_ans.replace('人回复','')
        if num_ans == '':	#若沒有醫生回覆
           num_ans ='0' #回覆數=0
        #print('回覆數:',num_ans)
        
        #用'問題編號 qnum'和'回覆數 num_ans'，判斷是否有重複的貼文和有沒有新的醫生回覆(舊資料)
        if qnum in nums: #若是重複的貼文
           if num_ans == nums[qnum][6]: #若'回覆數'一樣
              print('已存在:',qnum)
              continue			  		#則跳過這回(這筆問題)
           else:						#若'回覆數'不一樣
              del nums[qnum] 			#刪除該筆問題的舊的內容('askyiyu.csv')
              del doctors[qnum]			#刪除該筆問題舊的醫生資料('doctors.csv')
              print('已存在,有新回覆:', qnum)
        #用'問題編號 qnum'，判斷是否有重複的貼文,避免新問題出現，造成抓到重複的問題(這次執行抓的新資料)
        if qnum in new_nums: #若是重複的貼文
              print('已存在:',qnum)
              continue			  		#則跳過這回(這筆問題)
        print('抓取:', qnum) #抓取提示
        global total
        total += 1 #記錄抓取筆數
        new_nums.append(qnum) #記錄新抓的問題編號
		
        new_ask_info2 = new_ask_info[2].split(' ') #將標題後的資訊[性別、歲數、提問時間、多少人回覆]以' '切割	
        ask_box = ask.find_all('p', class_='crazy_new') #提問的內容
        answer_u = ask.find_all('span', class_='b_sp1') #有哪些醫生回覆
		
        dlinks = []
        for x in answer_u:
            info = x.find('a')
            if info != None:
              dlink = info.get('href') #醫生的個人資訊連結
              dlinks.append(dlink)     #用list儲存
              #print(dlink)
            else:
              dlinks.append('null')
              #print("該醫生沒有個人資訊頁面")
			  
        ask_answer = ask.find_all('div', class_='crazy_new') #醫生們回覆的內容	
        new_ask_box = ask_box[0].text.replace(' ','') #將提問內容去掉空白

		#醫生們的回覆
        if num_ans != '0': #若有醫生回覆
          n = 0
          contents = ''
          for j in ask_answer:    
              content = ''
              each = '' 
              j = str(j).replace('<br/>','</p><p>')
              j = BeautifulSoup(j, "lxml")
              for m in j.text:
                   if ord(m) not in [10,13,32,160]:
                      if ord(m) == 65306:
                         content = content[:len(content)-4] + content[len(content)-4:]		
                      content += m
	  
              new_ask_user = answer_u[n].text.strip()
              each = "(answer)\n"+"#"+new_ask_user+"#\n"+content+"\n"
              contents += each
              #doctor.csv 寫入
              #'問題編號', '問題連結','醫生名字','醫生個人資訊link'
              f2_csv.writerow([qnum, link, new_ask_user, dlinks[n]])
              n += 1
              if n == int(num_ans):
                 break
        else:	#若無醫生回覆
           contents = 'null' #回覆內容欄位=null
		   
		#askyiyu.csv寫入
		#'問題編號', '問題連結','提問人性別','提問人年齡','提問的標題','提問的內容','回覆數','醫生們的回覆'
        f_csv.writerow([qnum, link, new_ask_info2[0], new_ask_info2[2].replace('岁',''), new_ask_info[0], new_ask_box, num_ans, contents ]) 
        sleeptime = random.randint(1,3)
        print('休息時間',sleeptime,'秒')
        time.sleep(sleeptime) #隨機休息1~3秒

    print('第',a,'頁已抓取完成!')

def main():              
    for i in range(1,15): #控制抓取的頁數 range(x,y) ; x >= 1 , 2 <= y <=201
        run(i,20*(i-1))
        takeabreak = random.randint(5,10)
        print('放鬆',takeabreak,'秒')
        time.sleep(takeabreak) #隨機休息5~10秒
    		
    for key,value in nums.items(): 	#回填askyiyu.csv舊的已存在資料
        f_csv.writerow(value)
		
    for k,v in doctors.items():		#回填doctors.csv舊的已存在資料
        for k2,v2 in v.items():
            f2_csv.writerow(v2)
	
    f.close()
    f2.close()
    print('這次執行總抓取:',total,'筆')

if __name__ == '__main__':
    main()