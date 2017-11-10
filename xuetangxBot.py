import os
import json
import requests
#登陆
def login(usr,pwd):
    api="http://www.xuetangx.com/api/oauth2/access_token/"
    payload={
        'client_id':'5ef52de7bbbaa0080de8',
        'client_secret':'9389d21788c4b5e556b1fc7835667fec9917a8df',
        'username':usr,
        'grant_type':'password',
        'password':pwd
    }
    req = requests.post(api,data=payload)
    req_j=json.loads(req.text)
    if 'error' in req_j:
         raise Exception(req_j['error'])
    else:
        auth_header={
            'authorization': 'Bearer '+req_j['access_token'],
            'uid':str(req_j['uid'])
        }
        return auth_header
#获取课程列表
def getCoures(auth):
    api="http://www.xuetangx.com/api/v2/courses/enroll?course_type=0&offset=0&limit=6&course_status=ing"
    req = requests.get(api,headers=auth)
    req_j=json.loads(req.text)
    course_list=[]
    for x in req_j['courses']:
        course_list.append({
            'id':x['id'],
            'name':x['name']
            })
    return course_list
#获取章节列表
def getChapters(auth,course_id):
    api = "http://www.xuetangx.com/api/v2/course/%s/chapters?show_exams=false&show_sequentials=true"%(course_id)
    req = requests.get(api,headers=auth)
    req_j = json.loads(req.text)
    chapters=[]
    for chaper in req_j['chapters']:
        chaper_item=[]
        for subitem in chaper['sequentials']:
            chaper_item.append({
                'id':subitem['id'],
                'name':subitem['display_name']
                })
        chapters.append(chaper_item)
    return chapters
#获取章节视频链接列表
def getVideoUrls(auth,course_id,chapter_id):
    api = "http://www.xuetangx.com/api/v2/course/%s/sequential/%s/verticals"%(course_id,chapter_id)
    req = requests.get(api,headers=auth)
    req_j=json.loads(req.text)
    #print(req_j)
    video_urls=[]
    for videos in req_j['verticals']:
        for video in videos['children']:
            name = (videos['display_name'] if video['display_name'] == 'Video' else video['display_name'])
            if  name.strip() == '':
                name = videos['display_name']
            name = name.strip()
            api="http://www.xuetangx.com/api/v2/video/%s/20"%(video['source'])
            req = requests.get(api,headers=auth)
            req_j=json.loads(req.text)
            for video_url in req_j['sources']:
                video_urls.append({'url':video_url,'name':name})
    return video_urls
#下载视频
def downloadVideo(path,file,videoUrl):
    if not os.path.exists(path):
        os.makedirs(path)
    req = requests.get(videoUrl, stream=True)
    f = open("%s/%s"%(path,file), "wb")
    for chunk in req.iter_content(chunk_size=256):
        if chunk:
            f.write(chunk)
    f.close()

#填写你的账号
auth=login('usr','pwd')
#设置下载目录
base_path="d:\downloads"

fail_list=[]
#遍历已订阅课程
for coure in getCoures(auth):
    cur=0
    #遍历课程章节
    for chapters in getChapters(auth,coure['id']):
        cur+=1
        #遍历课程课程视频
        for chapter in chapters:
                for video in getVideoUrls(auth,coure['id'],chapter['id']):
                    path="%s/%s/第%d章/%s"%(base_path,coure['name'],cur,chapter['name'])
                    file="%s.mp4"%(video['name'])
                    print("正在下载 %s/第%d章/%s/%s"%(coure['name'],cur,chapter['name'],file))
                    try:
                        downloadVideo(path,file,video['url'])
                    except Exception as e:
                        fail_list.append("%s 第%d章 %s %s下载失败\n\t"%(coure['name'],cur,chapter['name'],video['url']))
for fail in fail_list:
    print(fail)
print("\n全部下载完毕")
