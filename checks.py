from math import *
from decimal import *
from Tkinter import *
import output
import tkFileDialog
import tkMessageBox

#def output.write(msg,tag,log):
#    numlines = log.index('end - 1 line').split('.')[0]
#    log['state'] = 'normal'
#    if numlines==24:
#        log.delete(1.0, 2.0)
#    if log.index('end-1c')!='1.0':
#        log.insert('end', '\n')
#    log.insert('end', msg,tag)
#    log['state'] = 'disabled'
    
    
def check_beams(Plan1,Plan2,passLog,failLog):
    plan_mismatch = False
    output.write('\n\nBEAM CHECK','CheckHeading',passLog)
    for x in range(Plan1.NumBeams):
        #output.write('\n********************','INFO',passLog)        
        output.write('\nBEAM \t %s' % Plan1.Beams[x].BeamName,'BeamHeading',passLog)
        output.write('Parameter\t\tLANTIS\t\tOTP','TabHeading',passLog)
        #output.write('********************\n','Heading',passLog)
                          
        # Check for mismatch in Beam dictionaries.
        for key in Plan1.Beams[x].__dict__:
            # Initialise beam mismatch flag
            beam_mismatch = False
            # Compare parameter values
            if Plan1.Beams[x].__dict__[key] != Plan2.Beams[x].__dict__[key]:
                # Segment checking
                if key == "Segments":
                    for k in range(Plan1.Beams[x].NumSegments):
                        output.write('\nSegment: %i' % (k+1),'SegHeading',passLog)
                        output.write('Parameter\t\tLANTIS\t\tOTP','TabHeading',passLog)

                        for segkey in Plan1.Beams[x].Segments[k].__dict__:
                            segment_mismatch = False
                            if Plan1.Beams[x].Segments[k].__dict__[segkey] != Plan2.Beams[x].Segments[k].__dict__[segkey]:
                                if segkey == "MLC":
                                    #for i in range(81):
                                    for i in range(41):
                                        logstring = ("MLC Pair %i\t\t[%0.2f %0.2f]\t\t[%0.2f %0.2f]" % (i+1,Plan1.Beams[x].Segments[k].MLC[i],Plan1.Beams[x].Segments[k].MLC[i+41], Plan2.Beams[x].Segments[k].MLC[i],Plan2.Beams[x].Segments[k].MLC[i+41]))
                                        if (fabs(Plan1.Beams[x].Segments[k].MLC[i] - round(Plan2.Beams[x].Segments[k].MLC[i],2)) > 0.011) or (fabs(Plan1.Beams[x].Segments[k].MLC[i+41] - round(Plan2.Beams[x].Segments[k].MLC[i+41],2)) > 0.011) :
                                            output.write('\nBEAM \t %s' % Plan1.Beams[x].BeamName,'BeamHeading',failLog)        
                                            output.write('Parameter\t\tLANTIS\t\tOTP','TabHeading',failLog)                
                                            output.write(logstring,'MLCFAIL',failLog)
                                            segment_mismatch = True
                                        else:
                                            output.write(logstring,'MLCPASS',passLog)
                                else:
                                    segment_mismatch = True  

                            if (segkey != "MLC"):
                                logstring = ("%s\t\t%s\t\t%s") %(segkey, Plan1.Beams[x].Segments[k].__dict__[segkey], Plan2.Beams[x].Segments[k].__dict__[segkey])
                                if not(segment_mismatch):
                                    output.write(logstring,'PASS',passLog)
                                else:
                                    plan_mismatch = True
                                    output.write('\nBEAM \t %s' % Plan1.Beams[x].BeamName,'BeamHeading',failLog)
                                    output.write('Segment: %i' % (k+1),'SegHeading',failLog)
                                    output.write('Parameter\t\tLANTIS\t\tOTP','TabHeading',failLog)                                      
                                    output.write(logstring,'FAIL',failLog)                                          
                                
                # If  beam names don't fully match, but do partially match, then do nothing
                elif(key == 'BeamName' and Plan1.Beams[x].BeamName in Plan2.Beams[x].BeamName):
                    pass
                elif(key == 'MLC'):
                    for i in range(41):
                        logstring = ("MLC Pair %i\t\t[%0.2f %0.2f]\t\t[%0.2f %0.2f]" % (i+1,Plan1.Beams[x].MLC[i],Plan1.Beams[x].MLC[i+41], Plan2.Beams[x].MLC[i],Plan2.Beams[x].MLC[i+41]))
                        if (fabs(Plan1.Beams[x].MLC[i] - round(Plan2.Beams[x].MLC[i],2)) > 0.011) or (fabs(Plan1.Beams[x].MLC[i+41] - round(Plan2.Beams[x].MLC[i+41],2)) > 0.011) :            
                            #logstring = ("MLC Leaf Number %i\t\t%f\t\t%f\t\t%f" % (i,Plan1.Beams[x].Segments[k].MLC[i], Plan2.Beams[x].Segments[k].MLC[i],(fabs(Plan1.Beams[x].Segments[k].MLC[i] - round(Plan2.Beams[x].Segments[k].MLC[i],2)))))
                            output.write('\nBEAM \t %s' % Plan1.Beams[x].BeamName,'BeamHeading',failLog)        
                            output.write('Parameter\t\tLANTIS\t\tOTP','TabHeading',failLog)                
                            output.write(logstring,'MLCFAIL',failLog)
                        else:
                            output.write(logstring,'MLCPASS',passLog)
#                    for i in range(0,81):
#                        # Run through MLC positions, check for differences exceeding rounding errors
#                        if (fabs(Plan1.Beams[x].MLC[i] - round(Plan2.Beams[x].MLC[i],2)) > 0.011):            
#                            logstring = ("MLC Leaf Number %i: %f %f %f " % (i,Plan1.Beams[x].MLC[i], Plan2.Beams[x].MLC[i],(fabs(Plan1.Beams[x].MLC[i] - round(Plan2.Beams[x].MLC[i],2)))))
#                            output.write(logstring,'FAIL',passLog)                                              
                else:
                    # Flag a mismatch and record which parameter failed in which beam
                    beam_mismatch = True
                    plan_mismatch = True

            if not(beam_mismatch) and not(key == "MLC"):
                logstring = ("%s\t\t%s\t\t%s") %(key, Plan1.Beams[x].__dict__[key], Plan2.Beams[x].__dict__[key])
                output.write(logstring,'PASS',passLog)
            elif not(key =="MLC"):
                output.write('\nBEAM \t %s' % Plan1.Beams[x].BeamName,'BeamHeading',failLog)        
                output.write('Parameter\t\tLANTIS\t\tOTP','TabHeading',failLog)                
                logstring = ("%s\t\t%s\t\t%s") %(key, Plan1.Beams[x].__dict__[key], Plan2.Beams[x].__dict__[key])
                output.write(logstring,'FAIL',failLog)       

    if(plan_mismatch):
        return False
    else:
        return True


def check_Pt(LPlan,OTPPlan,passLog):
    output.write('\nPATIENT DATA CHECK\n','CheckHeading',passLog)


def check_Ports(LPlan,passLog,failLog):
    output.write('\nPORTAL BEAM CHECK\n','CheckHeading',passLog)
    for field in LPlan.PortFields:
        output.write('\nBEAM \t %s' % field.BeamName,'BeamHeading',passLog)        
        if (field.MU == 1):
            output.write('MU: %i' %field.MU,'PASS',passLog)
        else:
            output.write('MU: %i' %field.MU,'FAIL',failLog)
        if (field.Energy == 6):
            output.write('Energy: %i' %field.Energy,'PASS',passLog)
        else:
            output.write('Energy: %i' %field.Energy,'FAIL',failLog)
        if (field.Dose == 0):
            output.write('Dose: %i' %field.Dose,'PASS',passLog)
        else:
            output.write('Dose: %i' %field.Dose,'FAIL',failLog)        
        
    
def check_Px(LPlan,OTPPlan,passLog,failLog):
    Px_mismatch = False
    output.write('\nPRESCRIPTION CHECK\n','CheckHeading',passLog)
    LDoseFr = 0         # Lantis total dose per fraction
    OTPDoseFr = 0       # OTP total dose per fraction

    for i in range(0,LPlan.NumBeams):
        #print "Beam Number %i" %i
        LDoseFr += LPlan.Beams[i].Dose
        OTPDoseFr += OTPPlan.Beams[i].Dose

    OTPDoseTotal = OTPDoseFr * OTPPlan.NumFractions
    
    #print "Lantis dose/fr = %i" %LDoseFr
    #print "OTP Total dose = %i" %OTPDoseTotal 

   # for prescription in LPlan.Prescriptions:
        #if (prescription.Site == LPlan.Site):                    
            # Check Lantis beam dose/fraction = Lantis Prescription dose/fraction
    if LDoseFr == LPlan.Prescription.DoseFraction:
        output.write("Lantis dose/beam matches Prescription: %i %i" %(LDoseFr,LPlan.Prescription.DoseFraction),'PASS',passLog)
        #print "Lantis Px dose matches %i %i" %(LDoseFr,LPlan.Prescriptions[0].DoseFraction)
    else:
        output.write("Lantis dose/beam and Prescription mismatch: %i %i" %(LDoseFr,LPlan.Prescription.DoseFraction),'FAIL',failLog)
        Px_mismatch = True

    # Check OTP beam dose/fraction = Lantis Prescription dose/fraction
    if OTPDoseFr == LPlan.Prescription.DoseFraction:
        output.write("OTP dose/beam matches Prescription: %i %i" %(OTPDoseFr,LPlan.Prescription.DoseFraction),'PASS',passLog)
        #print "OTP Px dose matches %i %i" %(OTPDoseFr,LPlan.Prescriptions[0].DoseFraction)
    else:
        output.write("OTP dose/beam and Prescription mismatch: %i %i" %(OTPDoseFr,LPlan.Prescription.DoseFraction),'FAIL',failLog)
        #print "OTP Px dose doesn't match %i %i" %(OTPDoseFr,LPlan.Prescriptions[0].DoseFraction)
        Px_mismatch = True        

    if OTPDoseTotal == LPlan.Prescription.DoseTotal:
        output.write("OTP total dose matches prescription: %i %i" %(OTPDoseTotal,LPlan.Prescription.DoseTotal),'PASS',passLog)
        #print "Lantis Px dose matches %i %i" %(LDoseFr,LPlan.Prescriptions[0].DoseFraction)
    else:
        output.write("OTP total dose and prescription mismatch: %i %i" %(OTPDoseTotal,LPlan.Prescription.DoseTotal),'FAIL',failLog)
        Px_mismatch = True
   
    if(Px_mismatch):
        return False
    else:
        return True 

def check_NumBeams(LPlan,OTPPlan,passLog,failLog):
    # Check same number of beams
    #print LPlan.NumBeams,OTPPlan.NumBeams
    if not (LPlan.NumBeams == OTPPlan.NumBeams):
        tkMessageBox.showwarning(
        "Mismatch", 
        "Plans contain unequal number of beams" 
         )
        return False
    else:
        return True
