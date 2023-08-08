import os
import sys
import threading
import logging
import shutil

exclude_list = ['\\Genshin Impact\\',
                '\\Sabbat Of The Witch OST\\',
                '\\極彩色\\',
                '\\Moments\\',
                '\\Speed Limit Soundtrack\\',
                '\\TouhouMystiaIzakaya OST\\',
                '\\彼はきっと魔法を使う。\\',
                '\\アルカリレットウセイ\\',
                '\\アンチサイクロン\\',
                '\\エルゴスム\\',
                '\\セイデンキ少女\\',
                'はるまきごはんVocal ver',
                '\\君の名は\\','\\天气の子\\',
                '\\DOLL\\','\\Sunny!!\\',
                '\\Obscure Questions\\',
                '\\キメラ\\',
                '\\ネオドリームトラベラー\\',
                '\\HUMAN\\','\\奇奇怪怪的音乐\\'
                ] # 同步时完全排除（反向检查时会被删除
ignore_list = ['SyncToy_'] #同步时忽略（在反向检查时也不会被删除

def convert_audio(source,target,bitrate='160k'):
    assert os.system('ffmpeg -nostdin -hide_banner -i "{}" -ab {} -map_metadata 0 -id3v2_version 3 -acodec libmp3lame "{}"'.format(source,bitrate,target))==0

def convert_lyrics(source,target,encoding='mbcs'):
    with open(source,'rb') as fp:
        lrc = fp.read()
    try:
        lrc = lrc.decode('utf-8')
    except UnicodeDecodeError:
        lrc = lrc.decode('mbcs')
    finally:
        with open(target,'w+',encoding=encoding,errors='replace') as fp:
            fp.write(lrc)

def main():
    fromfolder = os.path.normpath(os.path.abspath(input('From folder: ')))
    tofolder = os.path.normpath(os.path.abspath(input('To folder: ')))
    counter = {
        'audio':0,
        'lyrics':0,
        'skipaudio':0,
        'skiplrc':0,
        'pckerror':0,
        'nckerror':0,
        'deletefile':0,
        'deletefolder':0
        }
    #正检查
    print('================== 1st Check ==================')
    for fromroot,folders,files in os.walk(fromfolder):
        toroot = fromroot.replace(fromfolder,tofolder)
        for filename in files:
            try:
                fromfile = os.path.join(fromroot,filename)
                fromextension = os.path.splitext(filename)[-1].lower()
                if fromextension in ['.flac','.mp3','.wav','.aac','.m4a','.ogg']:
                    tofile = os.path.join(toroot,os.path.splitext(filename)[0]+'.mp3')
                    if os.path.exists(tofile) or sum([(i in fromfile) for i in exclude_list+ignore_list]):
                        print('Skip:',fromfile,'->',tofile)
                        counter['skipaudio'] += 1
                        continue
                    else:
                        print('Handling:',fromfile,'->',tofile)
                        if not os.path.exists(toroot):
                            os.makedirs(toroot,exist_ok=True)
                            print('Make dir:',toroot)
                        print('Calling FFmpeg:',fromfile,'->',tofile)
                        convert_audio(fromfile,tofile,bitrate='192k')
                        counter['audio'] += 1
                elif fromextension == '.lrc':
                    tofile = os.path.join(toroot,filename)
                    if os.path.exists(tofile) or sum([(i in fromfile) for i in exclude_list+ignore_list]):
                        print('Skip:',fromfile,'->',tofile)
                        counter['skiplrc'] += 1
                        continue
                    else:
                        if not os.path.exists(toroot):
                            os.makedirs(toroot,exist_ok=True)
                            print('Make dir:',toroot)
                        print('Transforming encoding:',fromfile,'->',tofile)
                        convert_lyrics(fromfile,tofile,encoding='mbcs')
                        counter['lyrics'] += 1
            except Exception as e:
                print('Error:',str(e))
                counter['pckerror'] += 1
    #逆检查
    print('================== 2nd Check ==================')
    for toroot,folders,files in os.walk(tofolder):
        fromroot = toroot.replace(tofolder,fromfolder)
        if not os.path.exists(fromroot) or sum([(i in toroot+'\\') for i in exclude_list]):
            shutil.rmtree(toroot)
            print('Remove:',toroot)
            counter['deletefolder'] += 1
            continue
        fromfilelist = os.listdir(fromroot)
        for filename in files:
            try:
                tofile = os.path.join(toroot,filename)
                base,extension = os.path.splitext(filename)
                flag = 0
                for expectedextension in ['.aac','.mp3','.flac','.wav','.lrc','.m4a','.ogg']:
                    expectfilename = base+expectedextension
                    if expectfilename in fromfilelist:
                        flag = 1
                if sum([(i in tofile) for i in exclude_list]):
                    flag = 0
                if sum([(i in tofile) for i in ignore_list]):
                    flag = 1
                if flag == 0:
                    os.remove(tofile)
                    print('Remove:',tofile)
                    counter['deletefile'] += 1
                else:
                    print('Ok:',tofile)
            except Exception as e:
                print('Error:',str(e))
                counter['nckerror'] += 1

    print('================== Check End ==================')
    #统计
    print('''同步音频：{audio} 个
跳过音频：{skipaudio} 个
同步歌词：{lyrics} 个
跳过歌词：{skiplrc} 个
删除文件：{deletefile} 个
删除文件夹：{deletefolder} 个
正检查出错：{pckerror} 个
逆检查出错：{nckerror} 个'''.format(**counter))

if __name__ == '__main__':
    main()
    os.system('pause')
