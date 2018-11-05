import sys, os, copy
import time
import tkinter.messagebox

def substract (st1,f1,st2,f2):
    #if st1 < f1:tkinter.messagebox.showinfo('','error in bed1 record start-finish')
    #elif st2 < f2:tkinter.messagebox.showinfo('','error in bed2 record start-finish')

    start1,finish1,start2,finish2 = st1,f1,st2,f2
    if finish1 == start1  and (start2 == finish1 or finish2 == finish1):  return []
    if   start1 <  start2 and finish1 > finish2: return [(start1,start2-1),(finish2+1,finish1)]
    elif start1 <  start2 and finish1 <= finish2 and finish1 >= start2: return [(start1,start2-1)]
    elif start1 >= start2 and finish1 >  finish2 and start1 <= finish2: return [(finish2+1,finish1)]
    elif start1 >= start2 and finish1 <= finish2: return[]
    else:return 0

def frCompare(s1, f1, toCompare = list()):
    """
    :param s1: start of tested locus
    :param f1: finish of tested locus
    :param toCompare: list of bedRecord's, if any other list - generates error
    :return: list of tuples with [0] -> start, [1] - > finish
    """
    tc,i = toCompare,0
    retb = [(s1,f1)]
    pfix = 1
    length = len(tc)


    while len(retb) > 0 and i < len(retb) and length > 0:
        s1,f1 = retb[i]
        if pfix < 1: pfix = 1
        for pos in range(pfix,length):

            s2,f2 = tc[pos].start, tc[pos].finish

            if f2 < s1: continue
            elif s2 > f1:  break
            elif(s1 <= s2 <= f1) or (s1 <= f2 <= f1) or (s1 > s2 and f1 <  f2):
                pfix = pos
                getsubs = substract(s1,f1,s2,f2);

                for tmp in reversed(getsubs): retb.insert(i+1,tmp)
                del retb[i]
                i -= 1
                break
        i+=1
    return retb

def toChrNumber(nm):
    CNames = {i:i for i in range(1, 25)}
    CNames.update({str(i): i for i in range(1, 25)})
    CNames.update({'X':23, 'x':23, 'Y':24, 'y':24})
    
    if nm in CNames: return CNames[nm]
    else: return 0


def RecOverlapp(s1=0, f1=0, s2=0, f2=0):

    if s1 == s2:
        if f1 == f2: return  [1, s1, f1,1]   # 1 оба равны
        elif f1 < f2:  return [1, s2, f1, 2, f1+1,  f2] # 2 общее начало, второй длиннее
        elif f1 > f2:  return [1, s1, f2, 3, f2+1, f1] # 3 общее начало, первый длиннее
    elif f1 == f2:
        if s1 < s2: return [1, s2, f1,4,s1,s2-1]      # 4 общий конец, первый начинается раньше
        elif s1 > s2: return [1, s1, f1,5,s2,s1-1]    # 5 общий конец, второй начинается раньше
    elif f1 == s2: return [1, f1, s2,6,s1,f1-1,s2+1,f2]      # 6 одним нуклеотидом первый раньше
    elif s1 == f2: return [1, f2, s1,7,s2,f2-1,s1+1,f1]      # 7 одним нуклеотидом второй раньше
    else:
        if   s1 < s2 and f1 > f2: return [1, s1, f1,9,s1,s2-1,f2+1,f1] # 8 второй  вложенный
        elif s1 > s2 and f1 < f2: return[1, s2, f2,8,s2,s1-1,f1+1,f2]  # 9 первый вложенный
        elif s1 < s2 and f1 < f2 and f1 > s2: return [1, s2, f1,10,s1,s2-1,f1+1,f2] # 10 наложение частью первый раньше
        elif s1 > s2 and f1 > f2 and f2 > s1: return [1, s1, f2,11, s2,s1-1,f2+1,f1] # 11 наложение частью второй раньше



class bedRecord:
    def __init__(self, chrn = 1, st = 0, en = 0,  bagg = "", num = 0):#, printflag = 0):
        if en >= st:
            self.start = st
            self.finish = en
            self.definition = bagg
            if chrn == 23:self.chrName = 'X'
            elif chrn == 24:self.chrName = 'Y'
            else: self.chrName = str(chrn)
            self.marked = 0
            self.numberinchr = num





    @property
    def number(self):
        return self.numberinchr

    @property
    def length(self):
        return (self.finish - self.start)

    @property
    def showSelf(self):
        return 'chr'+self.chrName+'\t'+str(self.start)+'\t'+str(self.finish)+'\t'+self.definition[:-1]

    def showFields(self, num=0, st=0, fin=0, defin = 0, separator = '\t'):
        ret = str()
        if num: ret += 'chr'+self.chrName+separator
        if st:  ret += str(self.start)+separator
        if fin:  ret += str(self.finish)+separator
        if defin:
            buf = self.definition.replace('\t','_')
            ret += buf#[:-1]
        return ret

class HumanBed:
    ChrNumbers = (i for i in range(1, 25))
    ChrNames =   tuple([str(i) for i in ChrNumbers] + ['X','x','Y','y'])
    def __init__(self):
        self._fullLength = 0;
        self._exome = [[i*c for i in range(1,2) if i > 0] for c in range(25)]
        self._exome[0]=[]

    def Cover(self, cname, testpos):
        if cname not in self.ChrNumbers and cname not in self.ChrNames: return 0
        else:
            for rec in self.Chromosome(toChrNumber(cname))[1:]:
                #print(rec)
                if rec.start <= testpos <= rec.finish: return rec.numberinchr
        return 0


    @property
    def bedName (self):
        return self._exome[0]

    def setName(self, bname=''):
        self._exome[0] = bname

    @property
    def getFullLength(self):
        return self._fullLength

    def haveRecord(self, cNum,rNum=1): #rewrited
        ret = 0
        if cNum in self.ChrNumbers:
            if len(self._exome[cNum]) > rNum: ret = 1
        return ret

    def Record(self, cNum,rNum=1): #rewrited
        if self.haveRecord(cNum, rNum) and cNum in self.ChrNumbers:
            return self._exome[cNum][rNum]
        else: raise NameError('Index out of range')

    def Chromosome(self, cNum): #rewrited
        if cNum in self.ChrNumbers: return self._exome[cNum]
        elif cNum in self.ChrNames:
            return self._exome[toChrNumber(cNum)]
        else: raise NameError('Index out of range')

    @property
    def AllBed (self):
        return self._exome[1:]

    def addRecord (self, nm , b):

        if type(b) == bedRecord:
            if nm in self.ChrNumbers:
                self._exome[nm].append(b)
                self._fullLength += 1

    def loadFromFile(self, fname = '', silentload = 0): # rewrited
        nBuf2 = 0
        stringbuf = ''
        names = self.ChrNames
        try:

            rdFile = open (fname, "r")
            #i = 0
            self._exome[0] = rdFile.readline()

            allText = rdFile.readlines(); rdFile.close()

            for sbuf in allText:

                if 'chr' in sbuf or 'Chr' in sbuf:
                    if '|' in sbuf and '\t' in sbuf: words = sbuf.replace('|','\t').split('\t')
                    elif '\t' in sbuf: words = sbuf.split('\t')
                    elif '|' in sbuf: words = sbuf.split('|')
                    else: print('Error in bed-file!'); continue

                    chrPreNum = words[0][3:]
                    if chrPreNum in names: chr_num = toChrNumber(chrPreNum)
                    else: print('Error in bed-file!'); continue

                    try: SPos, EPos = int(words[1]),int(words[2])
                    except ValueError: print("Error in bed-file!"); continue

                    recDefinition = '\t'.join(words[3:])

                    self.addRecord(chr_num,bedRecord(chr_num,SPos, EPos, recDefinition[:-1],self.chrLength(chr_num)+1))

                    nBuf1 = chr_num
                    if nBuf1 > nBuf2:
                        nBuf2 = nBuf1
                        if not silentload: print('$out$$amount2['+str(nBuf2)+'|'+'24]')


        except IOError: print("Cannot open file");

    def delRecord(self, chrnum = 1, number = 1): #rewrited
        if self.haveRecord(chrnum, number):
            del self._exome[chrnum][number];
   
    def chrLength(self, cn = 1): #rewrited
        if cn in self.ChrNumbers:
            return len(self._exome[cn])-1
        else: return 0

    def addRange(self, cn, rng):#, adList = 1):
        if type(rng) == list:            
            for i in rng[1:]:
                if type(i) != bedRecord: return 0
            if cn in self.ChrNumbers: self._exome[cn]+=rng;  self._fullLength += len(rng)

    def printToFile(self, fname):
        if type(fname) == str:
            try:
                svname = open(fname, 'w')
                svname.write(self.bedName+'\n')
                for currentchr in self._exome[1:]:
                    for brec in currentchr[1:]:
                        if brec.start == 0: tkinter.messagebox.showinfo('error,empty bedrecord',brec.showself); exit()
                        svname.write(brec.showSelf+'\n')

            except: print('Writing to file failed')
            svname.close()

def BedsCompare(bd1, bd2, partFlag = 1, minsize = 2): #accelerate as it done for frCompare

    if type(bd1) != HumanBed or type(bd2) != HumanBed : print ('incorrect arguments'); return 0

    uniqBed1,uniqBed2, sharedBed = HumanBed(),HumanBed(),HumanBed()

    if "track name=\"" in bd1.bedName.lower(): nbuf1 = bd1.bedName[bd1.bedName.lower().find("track name=\"")+12:bd1.bedName.lower().rfind("\" description")]
    elif "track name=" in bd1.bedName.lower(): nbuf1 = bd1.bedName[bd1.bedName.lower().find("track name=")+11:bd1.bedName.lower().rfind(" description")]
    else: nbuf1 = "BedFile1"
    if "description=\"" in bd1.bedName.lower(): dbuf1 = bd1.bedName[bd1.bedName.lower().find("description=\"")+13:]; dbuf1 = dbuf1[: dbuf1.find("\"")];
    elif "description=" in bd1.bedName.lower():
        dbuf1 = bd1.bedName[bd1.bedName.lower().find("description=")+12:];
        if 'type=' in dbuf1.lower(): dbuf1 = dbuf1[:dbuf1.lower().rfind(" type")];
    else: dbuf1 = "undescribed1"
    if "type=" in bd1.bedName.lower(): tbuf1 = "bedDetail"
    trackName1 = "track name=unique:{} description={} type={} ".format(nbuf1,dbuf1,tbuf1 )

    if "track name=\"" in bd2.bedName.lower(): nbuf2 = bd2.bedName[bd2.bedName.lower().find("track name=\"")+12:bd2.bedName.lower().rfind("\" description")]
    elif "track name=" in bd2.bedName.lower(): nbuf2 = bd2.bedName[bd2.bedName.lower().find("track name=")+11:bd2.bedName.lower().rfind(" description")]
    else: nbuf2 = "BedFile1"
    if "description=\"" in bd2.bedName.lower(): dbuf2 = bd2.bedName[bd2.bedName.lower().find("description=\"")+13:]; dbuf2 = dbuf2[: dbuf2.find("\"")];
    elif "description=" in bd2.bedName.lower():
        dbuf2 = bd2.bedName[bd2.bedName.lower().find("description=")+12:];
        if 'type=' in dbuf2.lower(): dbuf2 = dbuf2[:dbuf2.lower().rfind(" type")];
    else: dbuf2 = "undescribed2"
    if "type=" in bd2.bedName.lower(): tbuf2 = "bedDetail"
    trackName2 = "track name=unique:{} description={} type={} ".format(nbuf2,dbuf2,tbuf2 )

    trackNameSh = 'track name=overlap:{}_&_{} description={}_&_{} type=bedDetail'.format(nbuf1,nbuf2,dbuf1,dbuf2)

    stepsCounter = 0
    stepsAmount = 0
    for dd in range(1,25): stepsAmount += bd1.chrLength(dd)

    uniqBed1.setName(trackName1)
    uniqBed2.setName(trackName2)
    sharedBed.setName(trackNameSh)
    st1, fin1, st2, fin2,tmj,sumTm,averTm = 0,0,0,0,0,0,0


    for cNum in range(1,25):   #1

        stepsAmount, cLen_1, cLen_2 = bd1.chrLength(cNum),bd1.chrLength(cNum),bd2.chrLength(cNum)

        if cLen_1 > 0 and cLen_2 == 0: print('Unique range in bed1 found'); uniqBed1.addRange(cNum, bd1.Chromosome(cNum)[1:]); #allStepsCounter += bd1.chrLength(cNum)
        elif cLen_1 == 0 and cLen_2 > 0:  print('Unique range in bed2 found'); uniqBed2.addRange(cNum, bd2.Chromosome(cNum)[1:])
        elif cLen_1 > 0 and cLen_2 > 0:

            chr1Buffer, chr2Buffer = bd1.Chromosome(cNum), bd2.Chromosome(cNum); rNum1 = 1; sumTm = 0
            B2ChrLength = len(chr2Buffer)
            stepsCounter = 0

            print('$out$$clearbars')
            trimBuffer1 = {}
            trimBuffer2 = {}
            posFixer = 1
            posFixerInitiated = 1

            for temporary1 in chr1Buffer[1:]:

                tm0 = time.time()
                st1, fin1 = temporary1.start, temporary1.finish

                stepsCounter +=1

                if posFixer < 1: posFixer = 1
                for position in range(posFixer,B2ChrLength):
                    temporary2 = chr2Buffer[position]
                    st2,fin2  = temporary2.start, temporary2.finish
                    if fin2<st1:
                        if posFixerInitiated == 0: posFixerInitiated = 1;
                        continue
                    elif st2>fin1: break
                    elif (st1 <= st2 <= fin1) or (st1 <= fin2 <= fin1) or (st1 > st2 and fin1 <  fin2):
                        if posFixerInitiated == 1: posFixer = position; posFixerInitiated = 0

                        rec_overlap = RecOverlapp(st1,fin1,st2,fin2)#проверяем перекрытие
                        ss, sf, case = rec_overlap[1:4]
                        sharedBed.addRecord(cNum, bedRecord(cNum, ss,sf,temporary1.showFields(0,1,1,1,'_')+'|'+temporary2.showFields(0,1,1,1,'_'),1))
                        if partFlag:
                            if case == 1: temporary1.marked, temporary2.marked  = 2,2
                            elif case == 2 or case == 5:
                                trimBuffer2[temporary2.number] = frCompare(rec_overlap[4],rec_overlap[5],bd1.Chromosome(cNum))
                                temporary1.marked, temporary2.marked  = 1,1
                            elif case == 3 or case == 4:
                                trimBuffer1[temporary1.number] = frCompare(rec_overlap[4],rec_overlap[5],bd2.Chromosome(cNum))
                                temporary1.marked, temporary2.marked  = 1,1
                            elif case == 6 or case == 10:
                                trimBuffer1[temporary1.number] = frCompare(rec_overlap[4],rec_overlap[5],bd2.Chromosome(cNum))
                                trimBuffer2[temporary2.number] = frCompare(rec_overlap[6],rec_overlap[7],bd1.Chromosome(cNum))
                                temporary1.marked, temporary2.marked  = 1,1
                            elif case == 7 or case == 11:
                                trimBuffer2[temporary2.number] = frCompare(rec_overlap[4],rec_overlap[5],bd1.Chromosome(cNum))
                                trimBuffer1[temporary1.number] = frCompare(rec_overlap[6],rec_overlap[7],bd2.Chromosome(cNum))
                                temporary1.marked, temporary2.marked  = 1,1
                            elif case == 8:
                                trimBuffer1[temporary1.number] = frCompare(rec_overlap[4],rec_overlap[5],bd2.Chromosome(cNum))
                                trimBuffer1[temporary1.number] = frCompare(rec_overlap[6],rec_overlap[7],bd2.Chromosome(cNum))
                                temporary1.marked, temporary2.marked  = 1,1
                            elif case == 9:
                                trimBuffer2[temporary2.number] = frCompare(rec_overlap[4],rec_overlap[5],bd1.Chromosome(cNum))
                                trimBuffer2[temporary2.number] = frCompare(rec_overlap[6],rec_overlap[7],bd1.Chromosome(cNum))
                                temporary1.marked, temporary2.marked  = 1,1
                        else:
                            temporary1.marked,temporary2.marked = 3,3

                tm = time.time() - tm0
                #sumTm += tm
                #averTm = sumTm / rNum1


                print(str(round(tm,3))+' sec. '+'Matched: Chr.{} '.format(cNum)+ "Current locus: "+ str(rNum1) + ' of ' + str(cLen_1))
                outt = '$out$$amount1['+str(cNum-1)+'|'+str(24)+']'+'$amount2['+str(stepsCounter)+'|'+str(stepsAmount)+']'
                print(outt)

                rNum1 +=1


            for  tmpBR1 in chr1Buffer[1:]:
                if tmpBR1.marked == 0: uniqBed1.addRecord(cNum, tmpBR1)
                elif tmpBR1.marked == 1:
                    if tmpBR1.numberinchr in trimBuffer1: listOfTuples = trimBuffer1[tmpBR1.numberinchr] #берем список, содержащий туплы с  началами и концами
                    for StFin in listOfTuples: #вытаскиваем сами туплы
                        tmpST,tmpFIN = StFin #распаковываем туплы
                        trimRec = bedRecord(cNum,tmpST,tmpFIN,'[unique part of locus]'+tmpBR1.showFields(1,1,1,1,'_'),0)
                        if minsize <= trimRec.length: uniqBed1.addRecord(cNum,trimRec)



            for tmpBR2 in chr2Buffer[1:]:
                if tmpBR2.marked == 0: uniqBed2.addRecord(cNum, tmpBR2)
                elif tmpBR2.marked == 1:
                    if tmpBR2.numberinchr in trimBuffer2: listOfTuples = trimBuffer2[tmpBR2.numberinchr] #берем список, содержащий туплы с  началами и концами
                    for StFin in listOfTuples: #вытаскиваем сами туплы
                        tmpST,tmpFIN = StFin #распаковываем туплы
                        trimRec = bedRecord(cNum,tmpST,tmpFIN,'[unique part of locus]'+tmpBR2.showFields(1,1,1,1,'_'),0)
                        if minsize <= trimRec.length: uniqBed2.addRecord(cNum,trimRec)



        #cNum+=1

        sumTm=0
    print('$out$amount1['+str(24)+'|'+str(24)+']')
    print ('All done')

    return (sharedBed,uniqBed1,uniqBed2)




#============================================================================================================================

def main ():
   # sys.stdout = open('humanbed_for.log','w')
#    fname1 = 'ASE.bed'
 #   fname2 = 'IT.bed'

    fname1 = 'ASE.bed'
    fname2 = 'IT.bed'

    Bed1 = HumanBed()
    Bed2 = HumanBed()

    print('First bed loading...')
    Bed1.loadFromFile(fname1)
    print('Total loaded: ', Bed1.getFullLength)
    print('Second bed loading...')
    Bed2.loadFromFile(fname2)
    print('Total loaded: ', Bed2.getFullLength)
    print('All beds loaded!')

    for i in Bed1.AllBed:
        print(str(len(i)-1)+';', end = ' ')
    print('\n\r')
    for i in Bed2.AllBed:
        print(str(len(i)-1)+';', end = ' ')
    print('\n\r')
    


    sB,uB1,uB2 = BedsCompare(Bed1, Bed2)
    #BedsCompare(Bed1, Bed2, 24)

    sB.printToFile('sharedBed.deb')
    uB1.printToFile('uniqBed1.deb')
    uB2.printToFile('uniqBed2.deb')

    for i in sB.AllBed:
        print(str(len(i)-1)+';', end = ' ')
    print('\n\r')
    for i in uB1.AllBed:
        print(str(len(i)-1)+';', end = ' ')
    print('\n\r')
    for i in uB2.AllBed:
        print(str(len(i)-1)+';', end = ' ')
    print('\n\r')
    input('End of programm')

if __name__ == "__main__": main()
