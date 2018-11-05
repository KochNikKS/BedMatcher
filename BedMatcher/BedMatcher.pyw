import os,sys
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import hbed
import platform

UPPERCASE = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')

buffer1 = None
buffer2 = None

def UpAbr(st=''):
    buf = ''
    for i in st:
        if i in UPPERCASE: buf += i
    return buf

class TCons(tkinter.Text):
    global mw

    #timeOut = None
    stepOut1 = None
    stepOut2 = None
    #counter = 0
    def __init__(self,window):
        if type(window) == tkinter.Tk or type(window)==tkinter.Toplevel:
            tkinter.Text.__init__(self, window)
    def setOuts(self, so1, so2):
        #self.timeOut = to
        self.stepOut1 = so1
        self.stepOut2 = so2
    def flush(self):
        pass

    def write(self,variable):
        if str(variable)!='\n' and ('$out$' not in variable):
             self.insert('end', str(variable)+'\n')
             self.see('end')
             self.update()

        elif ('$out$' in str(variable)):
            if '$refresh$' in str(variable):
                self.update()

            #if ('$time[' in variable):
            #    try:
            #        ct = variable[variable.find('$time[')+6:variable.find(']')]
            #        uni = variable[variable.find(ct)+len(ct)+1:]
            #        if '$' in uni: uni = uni[:uni.find('$')]
            #        #tkinter.messagebox.showinfo(uni,str(ct))
            #        if  type(self.timeOut)== tkinter.Entry or type(self.timeOut) == ttk.Entry or type(self.timeOut) == tkinter.Text:
            #            self.timeOut.delete(0,'end')
            #            self.timeOut.insert('end','To cur. Chr: '+ str(ct)+' '+uni)
            #        elif type(self.timeOut) == tkinter.Label or type(self.timeOut) == ttk.Label:
            #            self.timeOut['text'] = 'To cur. Chr: '+ str(ct)+' '+uni
            #
            #    except: self.insert('end','Syntax-error or invalid receivers'+'\n')
            if ("$amount1[") in variable:
                try:
                    ca1 = variable[variable.find('$amount1[')+9:]
                    ca2 = ca1[ca1.find('|')+1:ca1.find(']')]
                    ca1 = ca1[:ca1.find('|')]
                    percent = int(int(ca1)/int(ca2) * 100)
                    position = self.stepOut1['value']
                    if position < percent:self.stepOut1['value']=percent
                    #tkinter.messagebox.showinfo(str(percent))
                except: pass#self.insert('end','Syntax-error or invalid receivers'+'\n')
                self.update()
            if ("$amount2[") in variable:
                try:
                    ca1 = variable[variable.find('$amount2[')+9:]
                    ca2 = ca1[ca1.find('|')+1:ca1.find(']')]
                    ca1 = ca1[:ca1.find('|')]
                    percent = int(int(ca1)/int(ca2) * 100)
                    position = self.stepOut2['value']
                    if position < percent: self.stepOut2['value']=percent
                    #tkinter.messagebox.showinfo(str(percent))
                except: pass#self.insert('end','Syntax-error or invalid receivers'+'\n')
                self.update()

            if '$cls' in variable: self.clear()
            if '$clearbars' in variable: self.clearbars()
    def clearbars(self):
        self.stepOut1['value'] = 0
        self.stepOut2['value'] = 0


    def clear(self):
        self.delete('1.0','end')
        self.stepOut1['value'] = 0
        self.stepOut2['value'] = 0
        self.update()

    def activate(self):
        self.saveout = sys.stdout
        sys.stdout = self

    def deactivate(self):
        if self.saveout is not None: sys.stdout = self.saveout

class App(object):
    MesWinCanBeClosen = int()
    x,y = 0,0
    bedNames = []
    shortNames = []    
    def __init__(self):
        self.HumBed1, self.HumBed2, self.sB,self.uB1,self.uB2 = None,None,None,None,None

        self.MesWinCanBeClosen = 1
        self.shortNames = ['Bed1','Bed2']
        self.root = tkinter.Tk()

        self.style = ttk.Style()
        if 'Windows-7' in platform.platform():
            self.style.theme_use('vista')
        else: self.style.theme_use('clam')
        cb1 = 0
        self.root.protocol('WM_DELETE_WINDOW', self.onExitSM)
        #self.root.attributes("-toolwindow", 1)
        self.root.resizable(width = False, height = False)
        self.cb = tkinter.Checkbutton(self.root)
        self.filelist1 = tkinter.Listbox(self.root)
        self.filelist2 = tkinter.Listbox(self.root)
        self.fNameBox1 = tkinter.Entry(self.root)
        self.fNameBox2 = tkinter.Entry(self.root)
        self.label1 = tkinter.Label(self.root)
        self.label2 = tkinter.Label(self.root)
        self.root.geometry('620x148+500+300')
        self.root.title('Bed matcher')        
        self.root.iconbitmap("BM.ico")
        self.root['bd'] = 0
        self.filelist1.configure(height = 9, width = 60, selectmode = 'SINGLE')
        self.filelist1['bd'] = 0
        self.filelist1.place(x = 0, y = 0)
        self.filelist1.bind("<Double-Button-1>",self.bedsChoose)

        self.filelist2.configure(height = 3, width = 42, selectmode = 'SINGLE', bd = 0)
        self.filelist2.place(x = 364, y = 0)
        self.filelist2.bind("<Double-Button-1>",self.bedsUnChoose)

        self.fNameBox1.configure(width=20,bd=0)
        self.fNameBox1.place(x = 365, y = 52)
        self.fNameBox1.insert(0, 'Bed1')
        self.fNameBox1.bind("<KeyRelease>",self.onChange)

        self.fNameBox2.configure(width=20,bd=0)
        self.fNameBox2.place(x = 365, y = 72)
        self.fNameBox2.bind("<KeyRelease>",self.onChange)
        self.fNameBox2.insert(0, 'Bed2')

        self.label1.configure(text = 'BED1 abbreviation')
        self.label1.place(x = 500, y = 50)
        self.label2.configure(text = 'BED2 abbreviation')
        self.label2.place(x = 500, y = 70)

        #кнопки
        self.dirSel = ttk.Button(self.root)
        self.dirSel.configure(width = '3')
        self.dirSel.place(x = 333, y = 2)
        self.dirSel.bind("<ButtonRelease-1>", )
        self.dirSel.configure(text = '. . .', command = self.DirSelect)
        self.comBut = ttk.Button(self.root, command = self.startComparison)
        self.loadBut = ttk.Button(self.root, command = self.loadButAction)
      #  self.agrBut = ttk.Button(self.root, )
        self.loadBut.configure(text = 'Load', width = 10)
        self.comBut.configure(text = 'Start', width = 10)
       # self.agrBut.configure(text = 'Aggregate', width = 10)
        self.loadBut.place(x = 365,y = 122)
        self.comBut.place(x = 434,y = 122)
        #self.agrBut.place(x = 550,y = 122)
        self.loadBut.config(state="disabled")
       # self.agrBut.config(state="disabled")
        self.comBut.config(state="disabled")

        self.im = tkinter.PhotoImage(file='Config.gif')
        self.optBut = ttk.Button(self.root)
        self.optBut.place(x = 586, y = 115)
        self.optBut.configure(image = self.im, command = self.CallOptions)


        #кнопки

        self.cb.configure(text="Use abbreviation to save generated BED's", variable=cb1,onvalue=1,offvalue=0)
        self.cb.select()
        self.cb.configure(state = 'disable')
        self.cb.place(x  = 365, y = 90)
        fL = os.listdir('.')
        for i in fL:
            if ('.bed' in i) or ('.BED' in i) or ('.Bed' in i):
                self.filelist1.insert('end',i)

        self.fr = tkinter.Frame(self.root, width = 620, height = 2, bg='black')
        self.fr.place(x = 0, y = 150)

        self.lab = tkinter.Label(self.root)
        self.lab.configure(text = '', bg = 'lightgray', width = 80, anchor='w', fg = 'darkred', font = ('arial',11,'bold'))
        self.lab.place(x = 1, y = 153)

        #self.staticEntry = ttk.Entry(self.root, justify = 'left', width = 24)
        #self.staticEntry.place(x = 468,y = 154)
        #elf.staticEntry.insert('end','Time')
        #elf.staticEntry.bind("<KeyPress>", lambda a: "break")

        self.l1 = tkinter.Label(self.root, text = 'overal progress').place(x= 530, y = 728)
        self.l2 = tkinter.Label(self.root, text = 'current progress').place(x= 530, y = 748)

        self.PBar1 = ttk.Progressbar(self.root, length = 530,  maximum = 100, mode = 'determinate', orient = "horizontal")
        self.PBar1.place(x = 1, y = 728)
        self.PBar1.bind('<1>', lambda a: messagebox.showinfo("","Processed: "+str(self.PBar1['value'])+'% of all locations'))

        self.PBar2 = ttk.Progressbar(self.root, length = 530,  maximum = 100, mode = 'determinate', orient = "horizontal")
        self.PBar2.place(x = 1, y = 748)
        self.PBar2.bind('<1>', lambda a: messagebox.showinfo("","Processed: "+str(self.PBar2['value'])+'% of curent chr'))


        self.cons = TCons(self.root)
        self.cons.configure(bg ="white", width = 75, height = 34,  borderwidth = 1, relief = 'groove')
        self.cons.place(x = 0,y = 180)
        self.cons.setOuts(self.PBar1, self.PBar2)

        self.cons.bind("<KeyPress>", lambda a: "break")

        self.menu = tkinter.Menu(self.root, tearoff=0)
        self.menu.add_command(label="copy to clipboard", command = self.copytoclipboard)
        self.cons.bind("<ButtonRelease-3>",self.popup)

        self.SB = ttk.Scrollbar(self.root)
        self.SB.configure(orient = 'vertical')
        self.SB['command'] = self.cons.yview
        self.cons['yscrollcommand'] = self.SB.set
        self.SB.place(x = 603, y = 180, height = 548)
        #====================================option window=======================
        self.optWindow = tkinter.Toplevel(self.root)
        self.optWindow.title('Options')
        self.optWindow.geometry('200x300+500+300')
        self.optWindow.iconbitmap("BM.ico")
        self.optWindow.iconbitmap("BM.ico")
        self.optWindow.attributes("-toolwindow", 1)
        self.optWindow.resizable(width = False, height = False)
        self.optFrame = tkinter.Frame(self.optWindow,height = 280, width = 180).place(x = 10, y = 10)

        self.partsCBvar = tkinter.IntVar()
        self.partsCB = tkinter.Checkbutton(self.optWindow, text = 'save unigue parts of shared loci')
        self.partsCB.configure(variable = self.partsCBvar,onvalue=1,offvalue=0,command = self.PCBCLICK)
        self.partsCB.deselect()
        self.partsCB.place(x = 4, y = 6)
        self.minPartVar = tkinter.IntVar()
        self.minPart = tkinter.Scale(self.optWindow,orient='vertical',length=250,from_= 2,to = 100, variable = self.minPartVar)
        self.minPart.place(x = 4, y = 35)
        self.mplabel = tkinter.Label(self.optWindow,text = 'Min. size of saved parts')
        self.mplabel.place(x = 60, y =  40)
        self.minPart.configure(state = 'disabled')
        self.optWindow.protocol('WM_DELETE_WINDOW', self.OWH)
        self.optWindow.withdraw()

        #===========================================================================
    def PCBCLICK(self, ):
        c = self.partsCBvar.get()
        if c == 1:self.minPart.configure(state = 'active')
        else: self.minPart.configure(state = 'disabled')

    def OWH(self):
        self.optWindow.withdraw()

    def copytoclipboard(self):
        try:
            self.cons.clipboard_clear()
            self.cons.clipboard_append(self.cons.selection_get())
        except:
            tkinter.messagebox.showerror('','Some text must be selected!')

    def popup(self, event):
        self.menu.post(event.x_root, event.y_root)

    def DirSelect(self):
        self.filelist1.delete(0,'end')
        st = tkinter.filedialog.askdirectory()
        if st == '': st = '.'
        fList = os.listdir(st)
        for i in fList:
            if ('.bed' in i) or ('.BED' in i) or ('.Bed' in i):
                self.filelist1.insert('end',i)

    def bedsChoose(self, event):
        if len(self.filelist1.curselection())>0:
            pos = int(self.filelist1.curselection()[0])
            if len(self.bedNames)<2 and self.filelist1.get(pos) not in self.bedNames:
                self.bedNames.append(self.filelist1.get(pos))

                if 0<len(self.bedNames): self.fNameBox1.delete(0,'end'); self.fNameBox1.insert('end', UpAbr(self.bedNames[0]))
                if 1<len(self.bedNames): self.fNameBox2.delete(0,'end'); self.fNameBox2.insert('end', UpAbr(self.bedNames[1]))
                if self.fNameBox1.get() == self.fNameBox2.get(): self.fNameBox1.insert('end','1'); self.fNameBox2.insert('end','2')

                self.filelist2.insert('end',self.filelist1.get(pos))
                if len(self.bedNames)>1:
                    self.loadBut.config(state = "active")
                    self.onChange(self,event)

    def bedsUnChoose(self, event):
        self.comBut.config(state = "disabled")
        if len(self.filelist2.curselection())>0:
            pos = int(self.filelist2.curselection()[0])
            self.bedNames.pop(pos)
            if len(self.bedNames) == 1:
                self.fNameBox2.delete(0,'end');
                self.fNameBox1.delete(0,'end');
                self.fNameBox1.insert('end', UpAbr(self.bedNames[0]))
                #self.fNameBox2.insert('end','Bed2')
            if len(self.bedNames) == 0:
                self.fNameBox1.delete(0,'end');
               # self.fNameBox1.insert('end', 'Bed1')

            self.filelist2.delete(pos,pos)
            if len(self.bedNames) < 2:
                self.loadBut.config(state = "disabled")

    def onExitSM(self):
        if self.MesWinCanBeClosen == 1: self.root.destroy()
        elif messagebox.askquestion("Window mustn't be closen now", 'Do You wand to terminate process and program?', icon = 'warning', type = 'yesno') == 'yes': self.root.destroy()

    def loadButAction(self):
        self.loadBut['state'] = 'disabled'
        self.cons.clear()
        self.comBut.config(state = "disabled")
        #======================================================
        self.HumBed1 = hbed.HumanBed()
        self.HumBed2 = hbed.HumanBed()
        #======================================================
        self.MesWinCanBeClosen = 0
        if len(self.bedNames)> 1:
            self.root.geometry('620x770+500+0')
            self.lab.configure(text = 'Loading. Please wait...')
            self.lab.update()


            self.cons.activate()
            self.HumBed1.loadFromFile(self.bedNames[0])
            self.PBar1['value'] = 50
            self.PBar2['value'] = 0
            self.HumBed2.loadFromFile(self.bedNames[1])
            self.PBar1['value'] = 100

            self.lab.configure(text = 'Both BEDs loaded', fg = 'darkgreen', bg = 'lightgray')
            self.lab.update()

            a = 'BED1 : '+self.HumBed1.bedName+'Total loci loaded: '+str(self.HumBed1.getFullLength)+'\n'
            a+='--------------------------------------------------------------------------'+'\n'
            a += 'BED2 : '+self.HumBed2.bedName+'Total loci loaded: '+str(self.HumBed2.getFullLength)+'\n'
            a+='--------------------------------------------------------------------------'+'\n'
            for i in range(1,25):
                a += 'Chr'+str(i)+ '\t'+ str(self.HumBed1.chrLength(i)) + '\t'
                a += str(self.HumBed2.chrLength(i)) + '\n'
            #tkinter.messagebox.showinfo('',a)
            print(a)
            self.cons.deactivate()
            self.comBut.configure(stat = 'active')
        self.MesWinCanBeClosen  = 1

    def onChange(self, event, num = 0):
        buf1 = self.fNameBox1.get()
        buf2 = self.fNameBox2.get()
        if buf1!='': self.shortNames[0] = buf1;
        else: self.shortNames[0] = 'Bed1'
        if buf2!='': self.shortNames[1] = buf2;
        else: self.shortNames[1] = 'Bed1'
        #tkinter.messagebox.showinfo(self.shortNames[0],self.shortNames[1])

    def startComparison(self):

        self.cons.clear()
        self.lab.configure(text='Overlap analysis. Please wait...',fg = 'darkred')
        self.comBut['state'] = 'disable'
        self.loadBut['state'] = 'disable'
        self.MesWinCanBeClosen = 0
        self.cons.activate()
        self.sB,self.uB1,self.uB2 = hbed.BedsCompare(self.HumBed1, self.HumBed2, self.partsCBvar.get(), self.minPartVar.get())

        #print (self.sB.AllBed)

        self.cons.deactivate()
        dirName = self.shortNames[0]+'-'+self.shortNames[1]
        if not os.path.exists(dirName):
            os.mkdir(dirName)

        relativePath = dirName+'\\'+ self.shortNames[0]+'+'+self.shortNames[1]

        self.sB.printToFile(relativePath+'_overlap.bedx')
        self.uB1.printToFile(relativePath+'_unique_of_'+self.shortNames[0]+'.bedx')
        self.uB2.printToFile(relativePath+'_unique_of_'+self.shortNames[1]+'.bedx')

        #self.aggregateBeds(dirName)

        self.lab.configure(text='Overlap analysis complete.',fg = 'darkgreen')
        self.loadBut['state'] = 'active'
        self.MesWinCanBeClosen = 1

    def CallOptions(self):
        self.optWindow.deiconify()




app = App()
app.root.mainloop()

#main()
