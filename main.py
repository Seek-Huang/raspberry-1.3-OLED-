#!/usr/bin/python
# -*- coding:utf-8 -*-
from config import SH1106
from PIL import Image,ImageDraw,ImageFont
import datetime
import calendar
import subprocess
import psutil
import re,os,json,requests
CLOCK_POS = (1, 0)
CPU_MEM_POS = (0,15)
POWER_POS = (0,53)
DISL_TEMP_POS = (0,25)
YIYAN_POS = (0,35)
frequency=0
font = ImageFont.truetype('config/Font.ttf', 13)
text_yiyan='获取中...'
def Load():
    disp = SH1106.SH1106()
    disp.Init()
    disp.clear()
    return disp
def clear(disp):
    disp.clear()
def load_image(disp,image):
    disp.ShowImage(disp.getbuffer(image))
def remark1(): #一言API
    global frequency
    global text_yiyan
    if frequency > 7:
       print('ok')
       frequency = 0
       text_yiyan = requests.get('https://v1.hitokoto.cn/?max_length=10&encode=text').content.decode('UTF-8')
       print(text_yiyan)
       return text_yiyan
def Power():
    text = round(float(subprocess.getoutput("echo 'get battery' | nc -q 0 127.0.0.1 8423")[8:]))
    text1 = subprocess.getoutput("echo 'get battery_power_plugged' | nc -q 0 127.0.0.1 8423")[22:].strip() 
    return  ' Pow:'+str(text)+'%    Cha:'+text1
def get_cpu_temp():
    return int(subprocess.getoutput('cat /sys/class/thermal/thermal_zone0/temp')) // 1000
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
         i = i + 1
         line = p.readline()
         if i == 2:
             return(line.split()[1:5])
def getCPUstate(interval=1):
  return (" CPU:"+str(psutil.cpu_percent(interval))+"%")
def getMemorystate():
  phymem = psutil.virtual_memory()
  line = " Mem:%5s%% %6s/%s"%(
      phymem.percent,
      str(int(phymem.used/1024/1024))+"M",
      str(int(phymem.total/1024/1024))+"M"
      )
  return line.strip()
def make_template(x,y): #创建位图并返回
    template = Image.new('1', (x, y), 0)
    draw = ImageDraw.Draw(template)
    return template
def render(template): #进一步在位图上添加内容
    image = template.copy()
    draw = ImageDraw.Draw(image)
    render_clock(draw)
    render_temp(draw)
    render_power(draw)
    render_disk_temp(draw)
    render_yiyan(draw)
    return image
def render_yiyan(draw):
    draw.text(YIYAN_POS,text_yiyan,font = font, fill=255)
def render_clock(draw): #显示时间及星期
    t = datetime.datetime.time(datetime.datetime.now())
    d = datetime.date.today() 
    day = str(d.day)
    month = str(d.month)
    weekday = calendar.day_name[d.weekday()]
    draw.text(CLOCK_POS, ' '+t.isoformat()[:5]+' '+day+'.'+month+' '+weekday,  fill=255)
def render_temp(draw):
    draw.text(CPU_MEM_POS, '{:>4} {}'.format(str(getCPUstate()), str(getMemorystate())), fill=255)
def render_power(draw):
    draw.text(POWER_POS,Power(), fill=255)
def render_disk_temp(draw):
    DISK_stats = getDiskSpace()
    DISK_perc = DISK_stats[3]
    draw.text(DISL_TEMP_POS, '{:>4} {}'.format(' Disk:'+str(DISK_perc), ' TEMP:'+str(get_cpu_temp())+u'°C'), fill=255)
if __name__ == "__main__":
    LINK=Load()
    template = make_template(LINK.width, LINK.height) #获取创建的位图
    while True:
        frequency+=1
        print(frequency)
        remark1()
        image = render(template) #获取最终处理图片,准备显示
        image.save('/tmp/test.jpg')
        try:
          load_image(LINK,image)
        except IOError as e:
            print(e)
        except KeyboardInterrupt:    
            print("ctrl + c:")
            epdconfig.module_exit()
            exit()
    sleep(1.5)

