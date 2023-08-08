import os
import csv
import sys
import time
import tinytag
import math

def ts2ymd(ts):
    t = time.localtime(ts)
    ymd = (t[0],t[1],t[2])
    return ymd

def analyze_fname(fname):
    path,fname = os.path.split(fname)
    fname,ext = os.path.splitext(fname)
    tmp = fname.split(' - ',1)
    if len(tmp) == 1:
        artists = []
        title = tmp[0]
    else:
        artists = tmp[0].split(',')
        title = tmp[1]
    return artists,title

def get_a_t(file,tag):
    artists = tag['artist']
    title = tag['title']
    jbfname = analyze_fname(file)
    if artists:
        artists = artists.split('/')
    else:
        artists = jbfname[0]
    if not title:
        title = jbfname[1]
    return artists,title

def hw2fw(text):
    # 半角转全角(仅转换文件名不支持的字符)
    rep_chr = {'/':'／','*':'＊',':':'：','\\':'＼','>':'＞',
              '<':'＜','|':'｜','?':'？','"':'＂'}
    for t in list(rep_chr.keys()):
        text = text.replace(t,rep_chr[t])
    return text
        
def get_ctime_map(path):
    earliest = 1577851200 # 2020年1月1日 # timestamp
    latest  = time.time() # timestamp
    cmap = {}
    for root,folders,files in os.walk(path):
        for file in files:
            _,ext = os.path.splitext(file)
            if ext.lower() in ['.m4a','.flac','.mp3','.ogg']:
                fullfile = os.path.join(root,file)
                tag = tinytag.TinyTag.get(fullfile)
                ctime = os.path.getctime(fullfile)
                if ctime < earliest:
                    earliest = ctime
                cmap[fullfile] = (
                    tag.as_dict(),
                    ctime
                    )
    return earliest,latest,cmap

def generate_stat(path,ref='total'):
    '''
    ref = total / artisttotal
    '''
    stat = {} # "%Y-%m-%d": value
    earliest,latest,cmap = get_ctime_map(path)
    current = earliest
    counter = 0
    cache = {}
    while current < latest:
        cymd = ts2ymd(current)
        date = "%d-%02d-%02d"%cymd
        #print(cymd,date)
        
        #counter = 0
        #cache = {}
        modi = False
        for file,value in cmap.items():
            tag,ctime = value
            ymd = ts2ymd(ctime)
            if ymd == cymd:
                counter += 1
                if ref == 'artisttotal':
                    artists,title = get_a_t(file,tag)
                    for a in artists:
                        a = hw2fw(a.strip())
                        if a in cache:
                            cache[a] += 1
                        else:
                            cache[a] = 1
                modi = True
        if modi:
            if ref == 'total':
                stat[date] = counter
            elif ref == 'artisttotal':
                stat[date] = cache.copy()

        current += 60*60*24
    return stat

def export(stat_dict,file,ref='total'):
    with open(file,'w+',encoding='utf-8-sig') as fp:
        fp.write('name,type,value,date\n')
        if ref == 'total':
            for date,value in stat_dict.items():
                fp.write('total,,%d,%s\n'%(value,date))
        elif ref == 'artisttotal':
            for date,tmp in stat_dict.items():
                for artist,value in tmp.items():
                    fp.write('%s,,%d,%s\n'%(artist,value,date))

def generate_makeup(d1,d2,ref):
    d1,v1 = d1
    d2,v2 = d2
    d1 = time.mktime(time.strptime(d1,'%Y-%m-%d'))
    d2 = time.mktime(time.strptime(d2,'%Y-%m-%d'))
    for a,v in v2.items():
        if not a in v1:
            v1[a] = 0
    makeups = {}
    reqgap = 60*60*24
    totalgap = d2-d1
    totalstep = math.floor(totalgap/reqgap)
    ts = d1
    for d in range(totalstep):
        ts += reqgap
        date = time.strftime("%Y-%m-%d",time.localtime(ts))
        if ref == 'total':
            makeups[date] = round(v1+(v2-v1)*(d/totalstep),2)
        elif ref == 'artisttotal':
            makeups[date] = {}
            for a,v in v2.items():
                kv = round(v1[a]+(v-v1[a])*(d/totalstep),2)
                makeups[date][a] = kv
    return makeups

def after_effect(stat,ref):
    dt,vt = 0,None
    makeups = {}
    for date,value in stat.items():
        if dt != 0:
            makeups.update(generate_makeup((dt,vt),(date,value),ref))
        dt,vt = date,value
    stat.update(makeups)
    return stat
        
if __name__ == '__main__':
    ref = input('total or artisttotal: ').lower()
    path = input('path: ')
    exfile = input('export file: ')
    stat = generate_stat(path,ref)
    #stat = after_effect(stat,ref)
    export(stat,exfile,ref)
