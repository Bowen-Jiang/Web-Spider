# Web-Spider

碩士論文的分支作品，為了蒐集使用者在有問必答網的抑鬱類別下的提問和醫生的回覆，自動解析網站並抓取資訊  
●	使用python (3.5.2) + Beautiful Soup (bs4)  
●	程式會輸出2個檔案askyiyu.csv和doctors.csv  
●	askyiyu.csv記錄每一篇使用者的提問  
‘問題編號’, ‘問題連結’,‘提問人性別’,‘年齡’,‘標題’,‘內容’,‘回覆數(醫生)’,‘醫生們的回覆內容'  
●	doctors.csv記錄每一篇提問，有哪些醫生回覆以及醫生個人資訊link  
'問題編號', '問題連結','醫生','醫生個人資訊link'  

提供以下功能  
● 自動判斷是否有新提問出現，避免重複抓取使用者的提問  
● 可以重複執行，累積資料  
● 若已抓取過的提問有新的醫生回覆也會更新  
