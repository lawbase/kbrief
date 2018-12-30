#
# krBrief.py
# 정부발간 보도자료 scrapping하는 것
# 현재 상태는 오늘 날짜와 어제 날짜를 가지고 URL을 구성하여 타이틀과 요약문을 가져옴
# 향후 전체 문서 pdf파일로 가져,
#

import requests
from bs4 import BeautifulSoup
import json 
import time
from datetime import date, timedelta, datetime
import sys  #arg command line argument 처리

#
# _____  krBrief 함수  _____
# 특정 일자 tDay 의 페이지 pageI 의 내용을 
# ans 라는 '리스트'에 담아서 리턴하는 함수
# return 값은 '리스트'에 담은 요수의 수
# 요수의 수가 39(실재로 40개) 이면 다음페이지로 넘어가게 설계하면 
# 특정 날짜의 보도자료를 모두 긇어서 json파일을 만들 수 있음
#

def krBrief(pageI, ans, tDay=date.today()) :
    #
    # 오늘날짜 와 어제 날짜를 가져옴
    #
    #tDay = date.today()
    yDay = tDay - timedelta(1)
    yyDay = tDay - timedelta(2)
    #pageI = 1
    URL_m = "http://www.korea.kr"
    URL_f = "/briefing/pressReleaseList.do?pageIndex=" + str(pageI) + "&srchRepCodeType=&repCodeType=&repCode="
    URL_b = "&endDate=" + str(tDay) + "&srchWord="
    # start , end 설정하는 방법으로 가져오기
    # URL_b = "&startDate=" + str(yDay) + "&endDate=" + str(tDay) + "&srchWord="
    # # 전체 보도자료를 가져오기 위해서는 starDate를 세팅하지 않으면 됨
    # URL_b = "&endDate=" + str(tDay) + "&srchWord=" 로 세팅하면 됨.

    #완전한 URL 생성
    URL = URL_m + URL_f + URL_b
    print(URL)
    #header 등 세팅
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    #cookies = {'session_id': 'sorryidontcare'}
    req = requests.get(URL, headers=headers)
    html = req.text

    # BeautifulSoup으로 html소스를 python객체로 변환하기
    # 첫 인자는 html소스코드, 두 번째 인자는 어떤 parser를 이용할지 명시.
    # 이 글에서는 Python 내장 html.parser를 이용했다.
    soup = BeautifulSoup(html, 'html.parser')

    #
    # 오늘자 보도자료의 title과 요약문을 찾음
    #
    titles = soup.select(".list_type01 ul li dl dt")
    conts = soup.select(".list_type01 ul li dl dd")
    '''
    #
    # List(json으로 변환될)를 담을 변수 선언
    #
    ans = [] 
    '''

    #
    # json 파일로 저장하기
    #
    for i, title in enumerate(titles):
        cont = conts[i*2+1].text.split()
        if ( (str(yDay.strftime("%Y.%m.%d")) == str(cont[1])) or (str(yyDay.strftime("%Y.%m.%d")) == str(cont[1])) ) :
            i = i - 1
            break
        #if (str(cont[1]) != str(tDay))
        sub_req = requests.get((URL_m + str(title.a["href"])), headers=headers)
        sub_html = sub_req.text
        sub_soup = BeautifulSoup(sub_html, 'html.parser')
        f_l = sub_soup.select(".filedown dl dd p")
        if (len(f_l) == 0): 
            file_name = "NoFile"
            file_link = "NoLink" 
        else:
            file_name = str(f_l[0].text.strip())
            file_link = URL_m + str(f_l[0].a["href"])
        print(file_name + "\t" + str(cont[1]))
        print(file_link)
        
        time.sleep(1)
        ans.append(
            {"제목":str(title.text), "내용":str(conts[i*2].text), "출처":str(cont[0]), "날짜":str(cont[1]), "파일이름":file_name, "파일링크":file_link}
            )
    return (i + 1)

#
# List(json으로 변환될)를 담을 변수 선언
#

#r_tDay = date.today()

#
# command line arg 처리
#
if len(sys.argv) is 1 : 
    print ("어제 날짜로 실행됩니다")
    r_tDay = date.today() - timedelta(1)
elif len(sys.argv) is 2 :
    r_tDay = datetime.strptime(sys.argv[1], "%Y-%m-%d").date() 
else :
    print ("arg - error!!")
    sys.exit(1)

res = 40
r_ans = []
r_pageI = 1 
while ( res >= 40 ) :
    print("페이지 : %d" % r_pageI)
    res = krBrief(r_pageI, r_ans, r_tDay)
    print(res)
    r_pageI = r_pageI + 1 


with open(str(r_tDay) + '.json','w') as fp: 
    fp.write(json.dumps(r_ans))



