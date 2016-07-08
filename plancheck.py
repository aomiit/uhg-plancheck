#!/usr/bin/python
# Filename : plancheck_11.py

from Tkinter import *
import Tkinter
import tkFileDialog
import tkMessageBox
import csv
import dicom
from math import *
from decimal import *
from pprint import pprint
import pdb

# Project Modules
import checks
import data
import output

# Set options for behaviour of Decimal function
getcontext().prec = 3

        
# Create GUI control for application
class Application(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()
        
        # Create Menus
        menubar = Menu(self)
        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load OTP Conformal Plan", command=lambda: self.OnOTPloadBtnClick("CRT"))
        filemenu.add_command(label="Load OTP IMRT Plan", command=lambda: self.OnOTPloadBtnClick("IMRT"))
        filemenu.add_separator()
        filemenu.add_command(label="Load Lantis Conformal Plan", command=lambda: self.OnLloadBtnClick("CRT"))
        filemenu.add_command(label="Load Lantis IMRT Plan", command=lambda: self.OnLloadBtnClick("IMRT"))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="Plans", menu=filemenu)
              
        self.config(menu=menubar)       
       
        # Create Status bar
        # Group  in a LabelFrame
        statusLogFrame = LabelFrame(self, text="Status", labelanchor="nw", font ='helvetica 10',width=50,padx=10,pady=10)
        self.labelVariable = Tkinter.StringVar()
        self.label = Tkinter.Label(statusLogFrame,textvariable=self.labelVariable,padx=400,pady=5,bg="light cyan",fg="black")
        
        resultsGroup = LabelFrame(self, text="Results", labelanchor="n",font='helvetica 12')
       
        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,True)
      
        # Create LabelFrame for  log
        passLogframe = LabelFrame(resultsGroup, text=" Passed Parameters", labelanchor="n", font ='helvetica 12',bd=0)
        passLogframe.grid(in_=resultsGroup,row=3,column=0, sticky=W)
        yscrollbar = Tkinter.Scrollbar(passLogframe)
        xscrollbar = Tkinter.Scrollbar(passLogframe,orient=HORIZONTAL)

        failLogframe = LabelFrame(resultsGroup, text=" Failed Parameters", labelanchor="n",font='helvetica 12',bd=0)
        yscrollbar2 = Tkinter.Scrollbar(failLogframe)
        xscrollbar2 = Tkinter.Scrollbar(failLogframe,orient=HORIZONTAL)


        # Create PASS log
        self.passLog = Tkinter.Text(passLogframe,state='disabled', width=57, height=20, wrap='none', foreground="red",background="light cyan",yscrollcommand=yscrollbar.set,xscrollcommand=xscrollbar.set)
        self.failLog = Tkinter.Text(failLogframe,state='disabled', width=57, height=20, wrap='none', foreground="red",background="light cyan",yscrollcommand=yscrollbar.set,xscrollcommand=xscrollbar.set)

        yscrollbar.config(command=self.passLog.yview)
        xscrollbar.config(command=self.passLog.xview)
        yscrollbar2.config(command=self.failLog.yview)
        xscrollbar2.config(command=self.failLog.xview)
        
        # Define font and colour settings for logs
        self.passLog.tag_config("PASS", foreground="forest green")
        self.passLog.tag_config("MLCPASS", foreground="forest green",font='helvetica 8')
        self.passLog.tag_config("MLCFAIL", background="red",font='helvetica 8',foreground='white')
        self.passLog.tag_config("FAIL", background="red",foreground="white")
        self.passLog.tag_config("INFO", foreground="black")
        self.passLog.tag_config('BeamHeading', foreground="darkgreen",font='helvetica 10 bold', relief='raised')
        self.passLog.tag_config('SegHeading', foreground="orchid3",font='helvetica 10 bold', relief='raised')
        self.passLog.tag_config('CheckHeading', foreground="maroon4",font='helvetica 10 bold', relief='raised')        
        self.passLog.tag_config('TabHeading', foreground="gray50",font='helvetica 10 bold', relief='raised')
        self.failLog.tag_config("PASS", background="forest green",foreground="black")
        self.failLog.tag_config("MLCPASS", foreground="forest green",font='helvetica 8')
        self.failLog.tag_config("MLCFAIL", foreground="red",font='helvetica 8')
        self.failLog.tag_config("FAIL", foreground="red")
        self.failLog.tag_config("INFO", foreground="black")
        self.failLog.tag_config('BeamHeading', foreground="darkgreen",font='helvetica 10 bold', relief='raised')
        self.failLog.tag_config('SegHeading', foreground="orchid3",font='helvetica 10 bold', relief='raised')
        self.failLog.tag_config('CheckHeading', foreground="maroon4",font='helvetica 10 bold', relief='raised')        
        self.failLog.tag_config('TabHeading', foreground="gray50",font='helvetica 10 bold', relief='raised')

 
        # Group OTP plan details in a LabelFrame
        OTPgroup = LabelFrame(self, text="OTP Plan", labelanchor="n",font='helvetica 10')
        
        # Variables used to update Patient/Plan data fields       
        self.otppatname = StringVar()
        self.otppatid = StringVar()
        self.otpplanid = StringVar()
        
        # Create Labels
        _OTPPatName = Tkinter.Label(OTPgroup, text="Patient Name",padx=10).grid(in_=OTPgroup, row=1,column=0,sticky=W)
        OTPPatName = Tkinter.Label(OTPgroup, textvariable=self.otppatname,bg='light cyan',relief=GROOVE,width=20).grid(in_=OTPgroup,row=1,column=2, sticky=EW)
        _OTPPatId = Tkinter.Label(OTPgroup, text="Patient ID",padx=10).grid(in_=OTPgroup, row=2,column=0,sticky=W)
        OTPPatID= Tkinter.Label(OTPgroup, textvariable=self.otppatid,bg='light cyan',relief=GROOVE,width=20).grid(in_=OTPgroup,row=2,column=2, sticky=EW)
        _OTPPlanID = Tkinter.Label(OTPgroup, text="Plan ID",padx=10).grid(in_=OTPgroup, row=3,column=0,sticky=W)
        OTPPlanID = Tkinter.Label(OTPgroup, textvariable=self.otpplanid,bg='light cyan',relief=GROOVE,width=20).grid(in_=OTPgroup,row=3,column=2, sticky=EW)        
        _OTPBeams = Tkinter.Label(OTPgroup, text="Beams",padx=10).grid(in_=OTPgroup, row=4,column=0,sticky="NW")
        self.OTPlog = Tkinter.Text(OTPgroup, state='disabled',width=25, height=10, wrap='none', foreground="red",bg="light cyan",relief=GROOVE)       
        self.OTPlog.tag_config("PASS", foreground="black")

        # Group Lantis plan details in a LabelFrame
        Lgroup = LabelFrame(self, text="Lantis Plan", labelanchor="n",font='helvetica 10')
        
        # Variables used to update Patient/Plan data fields       
        self.lpatname = StringVar()
        self.lpatid = StringVar()
        self.lplanid = StringVar()

        # Create and format Labels for Plan info
        _LPatName = Tkinter.Label(Lgroup, text="Patient Name",padx=10).grid(in_=Lgroup, row=1,column=0,sticky=W)
        LPatName = Tkinter.Label(Lgroup, textvariable=self.lpatname,bg='light cyan',relief=GROOVE,padx=10,width=20).grid(in_=Lgroup,row=1,column=2, sticky=EW)
        _LPatId = Tkinter.Label(Lgroup, text="Patient ID",padx=10).grid(in_=Lgroup, row=2,column=0,sticky=W)
        LPatID= Tkinter.Label(Lgroup, textvariable=self.lpatid,bg='light cyan',relief=GROOVE,padx=10,width=20).grid(in_=Lgroup,row=2,column=2, sticky=EW)
        _LPlanID = Tkinter.Label(Lgroup, text="Plan ID",padx=10).grid(in_=Lgroup, row=3,column=0,sticky=W)
        LPlanID = Tkinter.Label(Lgroup, textvariable=self.lplanid,bg='light cyan',relief=GROOVE,padx=10,width=20).grid(in_=Lgroup,row=3,column=2, sticky=EW)
        _LBeams = Tkinter.Label(Lgroup, text="Beams",padx=10).grid(in_=Lgroup, row=4,column=0,sticky="NW")
 
        self.RTPlog = Tkinter.Text(Lgroup,state='disabled', width=25, height=10, wrap='none', foreground="red",bg='light cyan',relief=GROOVE)
        self.RTPlog.tag_config("PASS", foreground="black")
        
        # Buttons
        OTPloadBtn_CRT = Tkinter.Button(OTPgroup,text=u"Load CRT",
                                command=lambda: self.OnOTPloadBtnClick("CRT"),width=10).grid(in_=OTPgroup,row=4,column=0,sticky="EW",padx=5)
        OTPloadBtn_IMRT = Tkinter.Button(OTPgroup,text=u"Load IMRT",
                                command=lambda: self.OnOTPloadBtnClick("IMRT"),width=10).grid(in_=OTPgroup,row=4,column=1,sticky="EW",padx=5)
      
        LloadBtn_CRT = Tkinter.Button(Lgroup,text=u"Load CRT",
                        command=lambda: self.OnLloadBtnClick("CRT"),width=10).grid(in_=Lgroup,row=4,column=0,sticky="EW",padx=5)
        
        LloadBtn_IMRT = Tkinter.Button(Lgroup,text=u"Load IMRT",
                        command=lambda: self.OnLloadBtnClick("IMRT"),width=10).grid(in_=Lgroup,row=4,column=1,sticky="EW",padx=5)

        CmpBtn = Tkinter.Button(self,text="Compare Plans",
                command=self.OnCmpBtnClick)
        QuitBtn = Tkinter.Button(self,text=u"Quit",
                command=self.OnQuitButtonClick)
 
        
        # Place items on grid cols=4 rows=9
        #self.rowconfigure(6, pad=20)
        #self.rowconfigure(7, pad=20)
        #self.columnconfigure(2, pad=20)


        resultsGroup.grid(row=4,column=0,columnspan=4,rowspan=3,sticky="EW",padx=10,pady=10)
        OTPgroup.grid(row=1,column=0,rowspan=3,sticky="EW",padx=10,pady=10)
        Lgroup.grid(row=1,column=2,rowspan=3,sticky="EW",padx=10,pady=10)        
        CmpBtn.grid(column=1,row=2,sticky="EW",ipady=20)
        #QuitBtn.grid(column=1,row=1,sticky="EW",ipady=20)
        #yscrollbar.grid(row=6, column=4,sticky="NS")
        #xscrollbar.grid(row=7, column=0,sticky="EW",columnspan=5)  
        yscrollbar.grid(row=0, column=2,sticky="NS")
        yscrollbar2.grid(row=0, column=4,sticky="NS")

        #xscrollbar.grid(row=1, column=0,sticky="EW",columnspan=5)       
        #OTPloadBtn_CRT.grid(column=0,row=0,sticky="EW")
        #OTPloadBtn_IMRT.grid(column=0,row=1,sticky="EW")
        #LloadBtn_CRT.grid(column=1,row=0,sticky="EW")
        #LloadBtn_IMRT.grid(column=1,row=1,sticky="EW")        
        self.OTPlog.grid(column=2,row=4,sticky="EW")       
        self.RTPlog.grid(column=2,row=4,sticky="EW")         
        passLogframe.grid(column=0,row=7,rowspan=1,columnspan=2)
        failLogframe.grid(column=2,row=7,rowspan=1,columnspan=2)
        self.passLog.grid(column=0,row=0,rowspan=1,columnspan=2,sticky="W")
        self.failLog.grid(column=2,row=0,rowspan=1,columnspan=2,sticky="W")

        #self.status.grid(column=0,row=6,sticky='E')
        statusLogFrame.grid(column=0,row=8,columnspan=5,sticky="EW",padx=10) 
        self.label.grid(in_=statusLogFrame,row=0,column=0,columnspan=4, sticky=EW)
        
       


    # Functionality for load OTP plan button        
    def OnOTPloadBtnClick(self,plantype):
        global Technique
        Technique = plantype
        # Clear previous info from result log window 
        self.passLog.config(state=NORMAL)
        self.passLog.delete(1.0, END)
        self.passLog.config(state=DISABLED)
        self.failLog.config(state=NORMAL)
        self.failLog.delete(1.0, END)
        self.failLog.config(state=DISABLED)
        # Reset info label
        self.label.config(bg='light cyan',fg='black')            
        self.labelVariable.set("Loading OTP Plan")
        # Create OTP plan object
        self.OTPPlan = data.Plan()
        
        #Technique = plantype
                
        # Read OTP plan
        OTPResult = self.OTPPlan.ReadOTP(self.OTPlog,Technique)
        self.otppatname.set(OTPResult[0])
        self.otppatid.set(OTPResult[1])
        self.otpplanid.set(OTPResult[2]) 
        #Update info label
        self.labelVariable.set("OTP Plan Loaded")
        #output.write("OTP plan loaded","INFO",self.passLog)        
        

        
    # Functionality for load Lantis plan button
    def OnLloadBtnClick(self,plantype):
        global Technique
        Technique = plantype
        # Clear previous info from result log window 
        self.passLog.config(state=NORMAL)
        self.passLog.delete(1.0, END)
        self.passLog.config(state=DISABLED)
        self.failLog.config(state=NORMAL)
        self.failLog.delete(1.0, END)
        self.failLog.config(state=DISABLED)
        # Reset info label
        self.label.config(bg='light cyan',fg='black')            
        self.labelVariable.set("Loading LANTIS Plan")
        output.write("Loading Lantis plan","INFO",self.passLog)
        self.LPlan = data.Plan()
        LResult = self.LPlan.ReadLantis(self.RTPlog,Technique)
        self.lpatname.set(LResult[0])
        self.lpatid.set(LResult[1])
        self.lplanid.set(LResult[2]) 
        self.labelVariable.set("Lantis Plan Loaded") 
        output.write("Lantis plan loaded","INFO",self.passLog)       

    # Compare plans
    def OnCmpBtnClick(self):        
        # Clear previous info from log window 
        self.passLog.config(state=NORMAL)
        self.passLog.delete(1.0, END)
        self.passLog.config(state=DISABLED)
        self.failLog.config(state=NORMAL)
        self.failLog.delete(1.0, END)
        self.failLog.config(state=DISABLED)

        # Check plans have the same number of beams
        if (checks.check_NumBeams(self.LPlan,self.OTPPlan,self.passLog,self.failLog)):
            if Technique == "CRT":
                # Check prescription
                if not (checks.check_Px(self.LPlan,self.OTPPlan,self.passLog,self.failLog)):                 
                    self.labelVariable.set("MISMATCH")
                    self.label.config(bg='red',fg='white')
                 
                #self.labelVariable.set("Checking Prescription")        
                #self.labelVariable.set("Comparing Plans")
            # If Lantis plan contains Port fields, check them
            if self.LPlan.PortFields:
                checks.check_Ports(self.LPlan,self.passLog,self.failLog)             
            # Check beams
            if (checks.check_beams(self.LPlan,self.OTPPlan,self.passLog,self.failLog)):
                self.labelVariable.set("Beams Matched")
                self.label.config(bg='green',fg='black')
            else:
                self.labelVariable.set("MISMATCH")
                self.label.config(bg='red',fg='white')                
        else:
            self.labelVariable.set("PLAN MISMATCH")
            self.label.config(bg='red',fg='white')


    def OnQuitButtonClick(self):
        self.destroy()    
    
   
# Main application loop
if __name__ == "__main__":
    app = Application(None)
    app.title('PlanCheck')
    app.mainloop()       

