import os,re,time

mode = input('Mode(0-Keyword,1-Regular):')

if mode.strip() == '0':

    files = os.listdir()
    reped = input('Str replaced:')
    rep = input('Str to replace:')

    for file in files:
        if file != file.replace(reped,rep):
            os.rename(file,file.replace(reped,rep))

elif mode.strip() == '1':

    files = os.listdir()

    regular = re.compile(input('Regular:'))
    rep = input('Str to replace:')

    for file in files:
        if file != re.sub(regular,rep,file):
            os.rename(file,re.sub(regular,rep,file))
