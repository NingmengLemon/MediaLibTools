import os
import sys
import threading
import logging
import shutil
import tinytag
import imghdr
from FileNameNormalizer import main as normalize_filename
import custom_adb as cadb
from NoMatchedLrcRemover import main as rm_unmatched_lrc

exclude_list = [
    ] # 同步时完全排除（反向检查时会被删除
ignore_list = ['SyncToy_'] #同步时忽略（在反向检查时也不会被删除

def convert_audio(source,target,bitrate='256'):
    additional_opts = []
    # 转移Tags
    try:
        tags = tinytag.TinyTag.get(source,image=True)
    except:
        pass
    else:
        if tags.title:
            additional_opts += ['--title "%s"'%tags.title.replace('"','""')] # 命令行双引号转义
        if tags.album:
            additional_opts += ['--album "%s"'%tags.album.replace('"','""')]
        if tags.albumartist:
            additional_opts += ['--band "%s"'%tags.albumartist.replace('"','""')]
        if tags.artist:
            additional_opts += ['--artist "%s"'%tags.artist.replace('"','""')]
        if tags.year:
            additional_opts += ['--date "%s"'%tags.year.replace('"','""')]
        if tags.genre:
            additional_opts += ['--genre "%s"'%tags.genre.replace('"','""')]
        #if tags.track:
        #    additional_opts += ['--track "%s"'%tags.track]
    # 封面
    try:
        cover = tags.get_image()
        if cover:
            with open('./temporary','wb+') as f:
                f.write(cover)
            ext = imghdr.what('./temporary')
            if ext:
                if os.path.exists('./temporary.'+ext):
                    os.remove('./temporary.'+ext)
                os.rename('./temporary','./temporary.'+ext)
            else:
                cover = None
    except:
        pass
    else:
        if cover:
            additional_opts += ['--artwork "%s"'%os.path.abspath('./temporary.'+ext)]
            
    pipe = 'ffmpeg.exe -nostdin -hide_banner -i "{}" -vn -sn -n -f wav -'.format(source)
    cmd = pipe + ' | ' + \
          'qaac.exe --threading -a {} {} -o "{}" - --ignorelength'.format(bitrate,' '.join(additional_opts),target)
    rv = os.system(cmd)
    assert rv==0,'Abnormal ReturnValue of os.system(): '+str(rv)

def convert_lyrics(source,target):#,encoding='mbcs'):
    possi_codec = ['utf-8','mbcs','gbk','ascii']
    with open(source,'rb') as fp:
        lrcb = fp.read()
    lrc = None
    for c in possi_codec:
        try:
            lrc = lrcb.decode(c)
        except UnicodeDecodeError:
            pass
        else:
            break
    if lrc:
        with open(target,'w+',encoding='utf-8') as fp:
            fp.write(lrc)
    else:
        print('Unable to convert lrc file:',source)

def main(fromfolder,tofolder):
    fromfolder = os.path.normpath(os.path.abspath(fromfolder))
    tofolder = os.path.normpath(os.path.abspath(tofolder))
    counter = {
        'audio':0,
        'lyrics':0,
        'skipaudio':0,
        'skiplrc':0,
        'pckerror':0,
        'nckerror':0,
        'deletefile':0,
        'deletefolder':0,
        'skipimg':0,
        'image':0
        }
    #正检查
    print('================== Straight Check ==================')
    for fromroot,folders,files in os.walk(fromfolder):
        print('Looking in',fromroot)
        toroot = fromroot.replace(fromfolder,tofolder)
        for filename in files:
            try:
                fromfile = os.path.join(fromroot,filename)
                fromextension = os.path.splitext(filename)[-1].lower()
                if fromextension in ['.flac','.mp3','.wav','.aac','.m4a','.ogg']:
                    tofile = os.path.join(toroot,os.path.splitext(filename)[0]+'.m4a')
                    if sum([(i in fromfile) for i in exclude_list+ignore_list]):
                        print('Skip:',fromfile,'->',tofile)
                        counter['skipaudio'] += 1
                        continue
                    if os.path.exists(tofile):
                        if os.path.getsize(tofile) > 0:
                            #print('Skip:',fromfile,'->',tofile)
                            counter['skipaudio'] += 1
                            continue
                        else:
                            os.remove(tofile)
                            print('Remove broken file:',tofile)
                    print('Handling:',fromfile,'->',tofile)
                    if not os.path.exists(toroot):
                        os.makedirs(toroot,exist_ok=True)
                        print('Make dir:',toroot)
                    print('Calling FFmpeg & QAAC:',fromfile,'->',tofile)
                    convert_audio(fromfile,tofile)#,bitrate='256k')
                    counter['audio'] += 1
                elif fromextension == '.lrc':
                    tofile = os.path.join(toroot,filename)
                    if os.path.exists(tofile) or sum([(i in fromfile) for i in exclude_list+ignore_list]):
                        #print('Skip:',fromfile,'->',tofile)
                        counter['skiplrc'] += 1
                        continue
                    else:
                        if not os.path.exists(toroot):
                            os.makedirs(toroot,exist_ok=True)
                            print('Make dir:',toroot)
                        print('Transforming encoding:',fromfile,'->',tofile)
                        convert_lyrics(fromfile,tofile)#,encoding='mbcs')
                        counter['lyrics'] += 1
                elif fromextension in ['.jpg','.jpeg','.bmp','.png','.gif']:
                    tofile = os.path.join(toroot,filename)
                    if os.path.exists(tofile) or sum([(i in fromfile) for i in exclude_list+ignore_list]):
                        #print('Skip:',fromfile,'->',tofile)
                        counter['skipimg'] += 1
                        continue
                    else:
                        shutil.copy(fromfile,tofile)
                        counter['image'] += 1
                        print('Copied image:',fromfile,'->',tofile)
            except Exception as e:
                print('Error:',str(e))
                counter['pckerror'] += 1
    #逆检查
    print('================== Reversed Check ==================')
    for toroot,folders,files in os.walk(tofolder):
        print('Looking in',toroot)
        fromroot = toroot.replace(tofolder,fromfolder)
        try:
            if not os.path.exists(fromroot) or sum([(i in toroot+'\\') for i in exclude_list]):
                shutil.rmtree(toroot)
                print('Remove:',toroot)
                counter['deletefolder'] += 1
                continue
        except Exception as e:
            print('Error:',str(e))
            counter['nckerror'] += 1
        fromfilelist = os.listdir(fromroot)
        for filename in files:
            try:
                tofile = os.path.join(toroot,filename)
                base,extension = os.path.splitext(filename)
                flag = 0
                for expectedextension in ['.aac','.mp3','.flac','.wav','.ogg','.lrc','.m4a','.jpg','.jpeg','.bmp','.png','.gif']:
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
                    pass
                    #print('Ok:',tofile)
            except Exception as e:
                print('Error:',str(e))
                counter['nckerror'] += 1

    print('================== Check End ==================')
    #统计
    print('''同步音频：{audio} 个
跳过音频：{skipaudio} 个
同步歌词：{lyrics} 个
跳过歌词：{skiplrc} 个
同步封面：{image}个
跳过封面：{skipimg}个
删除文件：{deletefile} 个
删除文件夹：{deletefolder} 个
正检查出错：{pckerror} 个
逆检查出错：{nckerror} 个'''.format(**counter))



def main_extra(fromfolder,tofolder):
    fromfolder = os.path.normpath(os.path.abspath(fromfolder)).replace('\\','/')
    tofolder = os.path.normpath(tofolder).replace('\\','/')
    fromfolder = '/'.join([i for i in fromfolder.split('/') if i!=''])
    tofolder = '/'+'/'.join([i for i in tofolder.split('/') if i!=''])

    stat = {
        'rmfile':0,
        'rmdir':0,
        'error':0
        }

    print('Pushing...')
    os.system('adb.exe push --sync "%s" "%s"'%(
        fromfolder,
        '/'.join(tofolder.split('/')[:-1])+'/'
        ))
    print('Verifying...')
    for toroot,dirs,files in cadb.walk_adb(tofolder):
        print('Looking in',toroot)
        fromroot = toroot.replace(tofolder,fromfolder)
        try:
            if not os.path.exists(fromroot):
                print('Delete:',toroot)
                rv = os.system('adb.exe shell rm -rf "%s"'%(cadb.linux_escape(toroot)))
                assert rv==0,'Abnormal Return Value: '+str(rv)
                stat['rmdir'] += 1
                continue # 删除远程文件夹
            for file in files:
                tofile = os.path.join(toroot,file).replace('\\','/')
                fromfile = os.path.join(fromroot,file).replace('\\','/')
                if not os.path.exists(fromfile):
                    print('Delete:',tofile)
                    rv = os.system(
                        'adb.exe shell rm -r "%s"'%(cadb.linux_escape(tofile)) # Linux字符转义
                        )
                    assert rv==0,'Abnormal Return Value: '+str(rv)
                    
                    # 删除远程文件
                    stat['rmfile'] += 1
        except Exception as e:
            print('Error:',str(e))
            stat['error'] += 1
    print('================== Sync End ==================')
    print('''删除文件：{rmfile} 个
删除目录：{rmdir} 个
错误个数：{error}'''.format(**stat))

if __name__ == '__main__':
    fromfolder = input('From folder: ')
    tofolder = input('To folder: ')
    if not fromfolder:
        fromfolder = r'D:\MUSIC'
    if not tofolder:
        tofolder = r'D:\LocalMusicLibForPhone'
    if input('你确定要执行音乐库同步("%s"->"%s")吗？输入114514以确认:'%(fromfolder,tofolder)).strip() == '114514':
        normalize_filename(fromfolder)
        rm_unmatched_lrc(fromfolder)
        main(fromfolder,tofolder)
        if input('\n直接按Enter开始Adb同步，输入任意内容按Enter退出.'):
            pass
        else:
            fromfolder = tofolder
            tofolder = input('RemoteTarget:')
            if not tofolder:
                tofolder = '/storage/emulated/0/LocalMusicLibForPhone/'
            while True:
                connected = cadb.check_connect()
                if len(connected) == 1:
                    break
                elif len(connected) >= 2:
                    print('连接的设备超过1个，断开多余的再试')
                else:
                    print('没有设备连接')
                input('按Enter重试')
            if input('你确定要执行音乐库同步("%s"->"%s")吗？输入1919810以确认:'%(fromfolder,tofolder)).strip() == '1919810':
                main_extra(fromfolder,tofolder)
            else:
                pass
    else:
        pass
    os.system('pause')
    sys.exit(0)
