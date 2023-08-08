# 此程序意在移除没有匹配的音乐文件的lrc文件
# 用os.walk()即可
# 要开学了没时间写先把文件创好

# 公元2023年6月22日, 终于想起要写这个程序
import os

possi_audio_ext = ['.flac','.mp3','.m4a','.aac','.wav','.ogg']

def split_filename(fn):
    split = os.path.splitext(fn)[0].split(' - ',1)
    if len(split) == 2:
        a,n = split
        a = a.split(',')
    else:
        n = split[0]
        a = []
    return a,n

def main(path):
    for root,folders,files in os.walk(path):
        lrcs = [i for i in files if i.lower().endswith('.lrc')]
        audios = [i for i in files if sum(
            [i.lower().endswith(o) for o in possi_audio_ext]
            )>0]
        audios_noext = [os.path.splitext(i)[0] for i in audios]
        for lrc in lrcs:
            if lrc[:-4] in audios_noext:
                continue
            flag = 0
            for audio in audios:
                lrc_a,lrc_n = split_filename(lrc)
                msc_a,msc_n = split_filename(audio)
                if lrc_n.lower() == msc_n.lower() and \
                   sum([i in msc_a for i in lrc_a]) >= len(msc_a)-2 and \
                   sum([i in lrc_a for i in msc_a]) >= len(lrc_a)-2:
                    flag = 1
                    break
            if flag == 0:
                df = os.path.join(root,lrc)
                print('Remove:',df)
                os.remove(df)
            
if __name__ == '__main__':
    path = input('Workdir:')
    main(path)
