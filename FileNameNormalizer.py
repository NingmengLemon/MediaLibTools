import os
import shutil
import unicodedata

def rp_fn(text):
    d = {
        '/':'／',
        '\\':'＼',
        ':':'：',
        '*':'＊',
        '?':'？',
        '"':'＂',
        '<':'＜',
        '>':'＞',
        '|':'｜'
        }
    for k,v in d.items():
        text = text.replace(k,v)
    return text

def main(path):
    for root,dirs,files in os.walk(path):
        for file in files:
            nfile = rp_fn(unicodedata.normalize('NFKC',file).strip())
            if nfile != file:
                os.rename(
                    os.path.join(root,file),
                    os.path.join(root,nfile)
                    )
                print('Normalized:',file)
                
if __name__=='__main__':
    path = input('WorkDir:')
    main(path)
        
