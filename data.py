'''
Created on 25 Jan 2012

@author: french_j
'''
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
import output

# TESTING
#global Technique 
global OTPfile
global RTPfile

#type = "IMRT"
#OTPfile = "P:/Trainee Med Phys/John/plancheck/plans/test.dcm"
#RTPfile = "P:/Trainee Med Phys/John/plancheck/plans/test.rtp"

#type = "CRT"
#OTPfile = "P:/Trainee Med Phys/John/plancheck/plans/test3.dcm"
#RTPfile = "P:/Trainee Med Phys/John/plancheck/plans/test3_edit.rtp"


class Plan:
    '''Imports and stores plan data.'''

   
    def __init__(self):
        self.Beams = []
        self.PortFields = []
        #self.Prescriptions = []

    def askopenfilename(self):
        """Returns a file name """

        filename = tkFileDialog.askopenfilename(**self.file_opt)
        if filename:
            return filename   
        
    def ReadOTP(self,log,plantype):
        '''Opens and parses a file in OTP DICOM format'''
        global DCMplan, Technique
        Technique = plantype
        beam_count = 0
  
       # define options for opening or saving DICOM file
        self.file_opt = options = {}
        options['defaultextension'] = '.DCM'
        options['filetypes'] = [('OTP DICOM','RP*.dcm'),('all files', '.*')]          
        options['title'] = 'Select DICOM file from OTP'        # File types to select in file open dialog     
        #options['initialdir'] = '..\plans'
        options['initialdir'] = 'C:\\OTP_DATA\DICOM\ExportTemp'
        #options['initialfile'] = 'myfile.txt'
        #options['parent'] = root


        OTPfile = self.askopenfilename()
        try:
            # use read_file method from dicom module to import plan into DCMplan object
            DCMplan=dicom.read_file(OTPfile)          
        except:
            tkMessageBox.showwarning(
                "Open file",
                "Cannot open this file\n(%s)" % filename
            )
         
                
        # extract patient/plan identifiers
        self.PatientsName = DCMplan.PatientsName        
        self.PatientID = DCMplan.PatientID
        self.Approval = DCMplan.ApprovalStatus

        self.PlanID = DCMplan.RTPlanName
        self.NumBeams = DCMplan.FractionGroups[0].NumberofBeams
        self.NumFractions = DCMplan.FractionGroups[0].NumberofFractionsPlanned

        # Clear previous plan info from log window 
        log.config(state=NORMAL)
        log.delete(1.0, END)
        log.config(state=DISABLED)
                    
        #message = "Patient: %s\nID:      %s" % (self.PatientsName,self.PatientID)
        #output.write(message,"Heading",log)
        #message = "Plan: %s\nBeams: %i" % (self.PlanID,self.NumBeams)
        #output.write(message,"Heading",log)

        # Load Beams from DICOM file
        for beam in DCMplan.Beams:
            new_beam = DCMBeam(beam,beam_count)
            beam_count += 1
            self.Beams.append(new_beam)
            output.write(beam.BeamName,"PASS",log)
        
        return(self.PatientsName,self.PatientID,self.PlanID)
        


    def ReadLantis(self,log,plantype):
        '''Opens and parses a file in Lantis RTP format''' 
        #print "TYPE = ", type
        global Technique
        Technique = plantype
        
        def LoadBeams():
			Pxselect.destroy()
			#pdb.set_trace()
			self.Site = selected.get()
			beam_index = -1
			beam_load = False
			''' Second pass through file.
			Load Beam, Control Point and Prescription data for selected prescription.'''
			with open(RTPfile, 'rb') as f:					 
				reader = csv.reader(f)						  # use csv module to parse file
				for row in reader:											  
					if ((row[0] == "FIELD_DEF") and (prescriptions.__contains__(row[1]))):
						# Check if beam number field is a number or string (ISO check)
						try:
							beam_num = int(row[3])  
							# Flag used to load next CONTROL_PT_DEF data
							beam_load = True
							beam_index += 1									
							beam = RTPBeam(row)						# create new beam object	
							self.Beams.append(beam)				 # append beam to list of beam objects
							output.write(str(row[2]),"PASS",log)
						except ValueError:										
							if (tkMessageBox.askyesno(
								"ISO Check field?", 
								"Is %s an ISO check field?" %str(row[2])
								 )):
								beam = RTPPortField(row)
								self.PortFields.append(beam)
								beam_load = False
							else:
								tkMessageBox.showwarning(
								 "Error",
								 "Can't proces beam %s\nCheck that beam ID is a number." %str(row[2]),
								 );
								self.NumBeams = beam_index + 1 
								return										   

					if (beam_load and Technique == "CRT"):
						if ((row[0] == "CONTROL_PT_DEF") and (int(row[1]) == self.Beams[beam_index].BeamNumber)):																	
							for i in range(32,73):								
								self.Beams[beam_index].MLC.append(round(float(row[i]),3))
							for i in range(132,173):
								self.Beams[beam_index].MLC.append(round(float(row[i]),3))								
						else:
							pass
					elif (beam_load and (Technique == "IMRT")):							
						if ((row[0] == "CONTROL_PT_DEF") and (int(row[1]) == self.Beams[beam_index].BeamNumber)):
							self.Beams[beam_index].NumSegments = int(row[4])/2
							if (int(row[5]) % 2 == 0):
								segMLC = []
								for i in range(32,73):								
									segMLC.append(round(float(row[i]),3))
								for i in range(132,173):
									segMLC.append(round(float(row[i]),3))
								segYjaws = [float(row[23]), float(row[24])]
							else:
								# Get actual segment cumulative MUs by multiplying fractional
								# cumulative MU from Lantis control point data by total beam MU
								CumulativeMU = float(row[7]) * self.Beams[beam_index].MU
								NewSegment = Segment(segMLC,segYjaws,CumulativeMU)
								self.Beams[beam_index].Segments.append(NewSegment)										
								NumCtrlPnts = row[4]
																																								  
					
					if ((row[0] == "RX_DEF") and (prescriptions.__contains__(row[2]))):
						self.Prescription = RTPPrescription(row)
						
						#Rx = RTPPrescription(row)
							#self.Prescriptions.append(Rx)								   

			self.NumBeams = beam_index + 1   
			
    						
        def CloseWindow():
            for x in range(len(prescriptions),0,-1):
                if not (selection[x-1].get()):							
                    del prescriptions[x-1]					 
            Pxselect.destroy()					
            LoadBeams()	

						        
        beam_index = -1
        prescriptions = []  # List of prescriptions in RTP file
        #Variable to record which prescription is selected from radiobutton
        selected = StringVar()
        selected.set('None') # initialize
        
       # define options for opening Lantis file
        self.file_opt = options = {}
        options['defaultextension'] = '.RTP' 
        options['filetypes'] = [('Lantis RTP','*.RTP'),('all files', '.*')]          
        options['title'] = 'Select RTP file from Lantis'
        #options['initialdir'] = '..\plans'        
        options['initialdir'] = 'L:\\NONIMAGE'
        #options['initialfile'] = 'myfile.txt'
        #options['parent'] = root        
                
      
        RTPfile = self.askopenfilename()

        if RTPfile:
            with open(RTPfile, 'rb') as f:                     
                reader = csv.reader(f)                          # use csv module to parse file
                ''' First pass through file.
                    Load Patient/Plan info, and identify prescriptions present.'''                
                for row in reader:                              # read RTP file row by row
                    if row[0] == "PLAN_DEF":                    # check for PLAN_DEF keyword
                        self.PatientID = row[1]                
                        self.PatientsName = row[3],row[2]
                        self.PlanID = row[5]

                        # Clear previous plan info from log window 
                        log.config(state=NORMAL)
                        log.delete(1.0, END)
                        log.config(state=DISABLED)

                        #message = "Patient:%s\nID:      %s" % (self.PatientsName,self.PatientID)
                        #output.write(message,"Heading",log)
                        
                    if row[0] == "RX_DEF":
                        #Rx = RTPPrescription(row)
                        prescriptions.append(str(row[2]))
                
                # Create window for Prescription selection
                Pxselect = Toplevel()
                Pxselect.title("Prescription")
                selection = list() 
                Label(Pxselect, text="""Select Lantis Prescription\n""", justify = LEFT,padx = 20).pack()

                for x in range(len(prescriptions)):
                    selection.append(IntVar())
                    Checkbutton(Pxselect, onvalue=1,offvalue=0,text=prescriptions[x], variable=selection[x],indicatoron=1,width=20,padx=20).pack() #,command=LoadBeams

                # Button to end prescription selection
                Button(Pxselect, text="Ok",padx=20,command=CloseWindow).pack()                
                
   		return(self.PatientsName,self.PatientID,self.PlanID)
   	             

                
                                   

                

                
# Beam parsing from RTP format
class RTPBeam:
    '''Stores beam parameters.'''
    def __init__(self,row):
        self.BeamName = str(row[2])      
        self.BeamNumber = int(row[3])  # PROBLEM WITH PORTAL FIELDS              
        self.Energy = float(row[11])
        self.GantryAngle = float(row[16])
        self.ColAngle = float(row[17])
        self.CouchAngle = float(row[29])
        self.SSD = float(row[15])                          
        self.MU = float(row[6])
        if Technique == "CRT":
            self.Dose = int(row[5])        
            self.Yjaws = [float(row[24]), float(row[25])]
            self.MLC = []
        
        if (Technique == "IMRT"):
            self.Segments = []
            
##        self.Xsize = float(row[19])
##        self.X1 = float(row[20])
##        self.X2 = float(row[21])
##        self.Ysize = float(row[23])
##        self.Y1 = float(row[24]) 
##        self.Y2 = float(row[25])

# Portal fields parsing from RTP format



class RTPPortField:
    '''Stores beam parameters.'''
    def __init__(self,row):
        self.BeamName = str(row[2])      
        self.BeamID = str(row[3])              
        self.Energy = float(row[11])
        self.GantryAngle = float(row[16])
        self.ColAngle = float(row[17])
        self.CouchAngle = float(row[29])
        self.SSD = float(row[15])                            
        self.Dose = int(row[5])
        self.MU = float(row[6])
        self.MLC = []
        self.Yjaws = [float(row[24]), float(row[25])]
##        self.Xsize = float(row[19])
##        self.X1 = float(row[20])
##        self.X2 = float(row[21])
##        self.Ysize = float(row[23])
##        self.Y1 = float(row[24]) 
##        self.Y2 = float(row[25])


# Beam parsing from DICOM format
class DCMBeam:
    '''Stores beam parameters.'''
    def __init__(self,beam,beam_count):
        #self.BeamNumber = beam_count + 1
        self.BeamNumber = beam.BeamNumber        
        self.BeamName = beam.BeamName
        self.Energy = beam.ControlPoints[0].NominalBeamEnergy
        self.GantryAngle = beam.ControlPoints[0].GantryAngle
        self.ColAngle = beam.ControlPoints[0].BeamLimitingDeviceAngle
        self.CouchAngle = beam.ControlPoints[0].PatientSupportAngle
        self.SSD = round(beam.ControlPoints[0].SourcetoSurfaceDistance/10,1)     
       
        if (Technique == "CRT"):
            # Round MUs to integers to match manual rounding done in Lantis    
            self.MU = round(DCMplan.FractionGroups[0].RefdBeams[beam_count].BeamMeterset,0)  
            self.Dose = round(DCMplan.FractionGroups[0].RefdBeams[beam_count].BeamDose*100,0)           
            self.MLC = []
            for i in range(0,82):            
                self.MLC.append(Decimal(beam.ControlPoints[0].BeamLimitingDevicePositions[1].LeafJawPositions[i])/Decimal(10))
            self.Yjaws = []
            for y in range(0,2):
                self.Yjaws.append(beam.ControlPoints[0].BeamLimitingDevicePositions[0].LeafJawPositions[y]/10)
                
        elif (Technique == "IMRT"):
            # Round MUs to one decimal place to match automatic rounding done in Lantis  
            self.MU = round(DCMplan.FractionGroups[0].RefdBeams[beam_count].BeamMeterset,1)
            self.Segments = []
            self.NumSegments = beam.NumberofControlPoints/2
            for j in range(self.NumSegments*2):
                # Even numbered control points contain field definitions 
                if ((j % 2) == 0):
                    # Initialise MLC and Yjaw lists   
                    segMLC = []                    
                    segYjaws = []                    
                    for i in range(0,82):            
                        segMLC.append(Decimal(beam.ControlPoints[j].BeamLimitingDevicePositions[1].LeafJawPositions[i])/Decimal(10))
                    for z in range(2):
                        segYjaws.append(beam.ControlPoints[j].BeamLimitingDevicePositions[0].LeafJawPositions[z]/10)
                # Odd numbered control points contain meterset information        
                else:
                    CumulativeMU = beam.ControlPoints[j].CumulativeMetersetWeight
                    # Create segment object and append to Beam segment list
                    NewSegment = Segment(segMLC,segYjaws,CumulativeMU)
                    self.Segments.append(NewSegment)
                
               
    
class Segment:
    def __init__(self,MLC,Yjaws,CumulativeMU):
        self.MLC = MLC
        self.CumulativeMU = round(CumulativeMU,1)
        self.Yjaws = Yjaws
            
        
class RTPPrescription:
    '''Stores dose prescription parameters'''
    def __init__(self,row):
        self.Course_ID = int(row[1])
        self.Site = str(row[2])
        self.Technique = str(row[3])
        self.Modality = str(row[4])
        self.DoseSpec = str(row[5])
        self.DoseTotal = int(row[7])
        self.DoseFraction = int(row[8])
        #self.NumBeams = int(row[11])
