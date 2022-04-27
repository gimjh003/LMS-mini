import requests
from bs4 import BeautifulSoup
import os.path

# url 설정
announce_url = "https://www.dju.ac.kr/dju/na/ntt/selectNttList.do?mi=1188&bbsId=1040"
scholarship_url = "https://www.dju.ac.kr/dju/na/ntt/selectNttList.do?mi=3957&bbsId=1853"
schedule_url = "https://www.dju.ac.kr/dju/sv/schdulView/schdulCalendarView.do?mi=1166"

# 게시판 정보 가져오기 [제목, 게시일, 링크, 조회수]
def get_content(url):
    res = requests.get(url)
    res.raise_for_status()
    html = BeautifulSoup(res.text, "lxml")
    contents = html.find("div", attrs={"class":"BD_list"}).find("tbody").find_all("tr")
    content_list = []
    for content in contents:
        content_title = content.find("a").get_text().strip()
        content_date = content.find_all("td")[3].get_text()
        content_id = content.find("a").attrs["data-id"]
        content_view = int(content.find_all("td")[4].get_text())
        content_url = f"https://www.dju.ac.kr/dju/na/ntt/selectNttInfo.do?nttSn={content_id}&bbsId=1040&mi=1188"
        if os.path.isfile("ignore.txt"):
            with open("ignore.txt", "r") as file:
                lines = file.readlines()
                for content in lines:
                    if(lines.split(", ")[0]) == content_title: continue
        else: pass
        content_list.append([content_title, content_date, content_url, content_view])
    return content_list

# 공지사항
def get_announce():
    announce_list = get_content(announce_url)
    return announce_list

# 장학
def get_scholarship():
    scholarship_list = get_content(scholarship_url)
    return scholarship_list

# 학사일정 [] = 연, [] = 월, [순서, 날짜정보, 일정]
schedule_res = requests.get(schedule_url)
schedule_res.raise_for_status()
schedule_html = BeautifulSoup(schedule_res.text, "lxml")
schedule_contents = schedule_html.find("ul", attrs={"id":"schedule_month"}).find_all("div", attrs={"class":"schedule_calendar"})
schedule_year = []
def get_schedule():
    for schedule in schedule_contents:
        schedule_info = schedule.find_all("tbody")[1].find_all("tr")
        for schedule_detail in schedule_info:
            schedule_date = schedule_detail.find("td", attrs={"class":"ac first"}).get_text()
            schedule_label = schedule_detail.find("ul", attrs={"class":"list_st3"}).get_text()
        schedule_year.append([schedule_date, schedule_label])
    return schedule_year

# 정렬
def sort_by_view(arr):
    for i in range(len(arr)-1):
        for j in range(len(arr)-1-i):
            if arr[j][3] < arr[j+1][3]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# 선착순 확인
def check_limited(arr):
    url = arr[2]
    res = requests.get(url)
    res.raise_for_status()
    html = BeautifulSoup(res.text, "lxml")
    if "선착순" in html.find("td", attrs={"colspan":"4"}).get_text(): return True
    else : return False

def collect_limited(arr):
    result = []
    for content in arr:
        if check_limited(content):
            result.append(content)
    return result

# 무시하기
def ignore(arr):
    if os.path.isfile("ignore.txt"):
        lines = [str(arr)[1:-1]+"\n"]
        with open("ignore.txt", "r", encoding="utf8") as file:
            lines.extend(file.readlines())
        with open("ignore.txt", "w", encoding="utf8") as file:
            for i in lines:
                file.write(i)
    else:
        with open("ignore.txt", "w", encoding="utf8") as file:
            file.write(f"{arr[0]},{arr[1]},{arr[2]},{arr[3]}\n")