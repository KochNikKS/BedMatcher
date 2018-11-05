import hbed
import tkinter
from tkinter import filedialog
from tkinter import messagebox
import cProfile, pstats

def main():
    ext = ''
    cnt = 0
    filtered = []
    buffer = []
    while ext != 'bed':
        bedfile = tkinter.filedialog.askopenfile(mode='r')
        if bedfile == None : exit()
        else:
            ext = bedfile.name[bedfile.name.rfind('.')+1:]
            ext.lower()
            if ext != 'bed': tkinter.messagebox.showinfo('Unacceptable file type','Choosen file extention is: ' + ext)


    filterBed = hbed.HumanBed()
    filterBed.loadFromFile(bedfile.name, silentload = 1)
    bedname = bedfile.name[bedfile.name.rfind('/')+1:]

    ffname = "CML-out.txt"
    filetofilter = open (ffname, 'r')
    targetFileName = open("CML-out_filtered_by_"+bedname+".txt",'w')
    fulltext = filetofilter.readlines()
    tkinter.messagebox.showinfo('',fulltext[0])
    #targetFileName.write(fulltext[0])
    filetofilter.close()

    for current_line in fulltext:
        cnt  += 1

        cc = cnt/len(fulltext)*100
        if cc%5 < 0.001: print('Processed: ',int(cc),'%')

        c = current_line.split('\t')
        if filterBed.Cover(c[9],int(c[10])): buffer.append(str(current_line))


    for current_line in buffer:
        targetFileName.write(current_line)
    targetFileName.close()

cProfile.run('main()', "profileresults.log")
p = pstats.Stats('profileresults.log')
p.strip_dirs().sort_stats('cumtime').print_stats()