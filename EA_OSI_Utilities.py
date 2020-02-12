

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
import time as t
import datetime
import random
import os, shutil
import subprocess
import csv
import EA_HL_UI_Utilities as UI
import EA_HL_RW_Utilities as RW
from itertools import repeat
from collections import Sequence
from disney_common import FCN


EACache='/eos/experiment/ship/user/ffedship/EA_V2/EA_Full_cache.csv'
EAIniPop='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_IPO.csv'
EAGen='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_GEN.csv'
LLTasks='/eos/experiment/ship/user/ffedship/EA_V2/Tasks_LL.csv'
HLTasks='/eos/experiment/ship/user/ffedship/EA_V2/Tasks_HL.csv'
LOG='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_Log.csv'
DATALOG='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_Data_Log.csv'
RESULT='/eos/experiment/ship/user/ffedship/EA_V2/EA_ONE_SHOT.csv'
_=0


def SubmitJobsCondor(FSB,Sample):
    Suitors=RW.ReadCsvData(LLTasks,'ReadLLTasks',59)
    JobNumber=0
    for p in range(0, len(Suitors)):
        if Suitors[p][57]==0 or (Suitors[p][57]==1 and (Suitors[p][58]>=6 or FSB=='Y')):
            JobNumber+=1
            SHName='/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/SH/SH_'
            SUBName='/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/SUB/SUB_'
            MSGName='MSG_'
            OptionLine='--mp '+"'"
            for elem in range(0,56):
                OptionLine+=(str(int(Suitors[p][elem]))+',')
                SHName+=(str(int(Suitors[p][elem]))+'_')
                SUBName+=(str(int(Suitors[p][elem]))+'_')
                MSGName+=(str(int(Suitors[p][elem]))+'_')
            OptionLine+=str(int(Suitors[p][56]))
            SHName+=(str(int(Suitors[p][56]))+'.sh')
            SUBName+=(str(int(Suitors[p][56]))+'.sub')
            MSGName+=str(int(Suitors[p][56]))
            f = open(SUBName, "w")
            f.write("executable = "+SHName)
            f.write("\n")
            f.write("output =/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/MSG/"+MSGName+".out")
            f.write("\n")
            f.write("error =/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/MSG/"+MSGName+".err")
            f.write("\n")
            f.write("log =/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/MSG/"+MSGName+".log")
            f.write("\n")
            f.write('requirements = (CERNEnvironment =!= "qa")')
            f.write("\n")
            f.write('transfer_output_files = ""')
            f.write("\n")
            f.write('+JobFlavour = "workday"')
            f.write("\n")
            f.write('queue 1')
            f.write("\n")
            f.close()
            if Sample=='D':
              TotalLine='python /afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/EA_LL_FCN_DUMMY.py '+OptionLine+"'"
            if Sample=='F':
              TotalLine='python /afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/EA_LL_FCN_FULL.py '+OptionLine+"'"
            if Sample=='R':
              TotalLine='python /afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/EA_LL_FCN.py '+OptionLine+"'"
            else:
                print 'Unrecognised sample'
            f = open(SHName, "w")
            f.write("#!/bin/bash")
            f.write("\n")
            f.write("source /afs/cern.ch/user/f/ffedship/private/SHIP/FairShipRun/config.sh")
            f.write("\n")
            f.write("set -ux")
            f.write("\n")
            f.write(TotalLine)
            f.write("\n")
            f.close()
            subprocess.call(['condor_submit',SUBName])
            print UI.TimeStamp(), bcolors.OKBLUE+"HT_HL_EA_FCN Message: Job ",TotalLine," has been successfully submitted"+bcolors.ENDC
            Suitors[p][57]=1
            if Suitors[p][58]>=6 or FSB=='Y':
                Suitors[p][58]=0
    if JobNumber>0:
       print UI.TimeStamp(), bcolors.OKBLUE+"Batch of ",JobNumber," jobs has been successfully sent to the cluster"+bcolors.ENDC
    if JobNumber==0:
        print UI.TimeStamp(), bcolors.FAIL+"No jobs to submit to HTCondor so far"+bcolors.ENDC
    Cash_output=open('/eos/experiment/ship/user/ffedship/EA_V2/Tasks_LL.csv',"w")
    Cash_writer = csv.writer(Cash_output)
    for op in range(0,len(Suitors)):
            Cash_writer.writerow(Suitors[op])
    Cash_output.close()
def CheckResults():
       HL_Meta_Jobs=RW.ReadCsvData(HLTasks,'ReadHLTasks',58)
       HL_Jobs=RW.ReadCsvData(HLTasks,'ReadHLTasks',56)
       LL_MetaPoints=RW.ReadCsvData(LLTasks,'ReadLLTasks',59)
       LL_Points=RW.ReadCsvData(LLTasks,'ReadLLTasks',57)
       LL_RedPoint=RW.ReadCsvData(LLTasks,'ReadLLTasks',56)
       JobsForHL=[]
       #We extract file names that we have to search for
       X_new=[]
       DeleteList=[]
       for p in range(0,len(HL_Jobs)):
           Length=[]
           Weight=[]
           Muon_w=[]
           FaultMuon_w=[]
           FitnessFunction=100000000
           IncompleteStatus=False
           for smpl in range (1,17):
               FCNPoint=[]
               Config_Name='/eos/experiment/ship/user/ffedship/EA_V2/Output/Config_'
               for n in range(0,56):
                  Config_Name+=(str(HL_Jobs[p][n])+'_')
                  FCNPoint.append(float(HL_Jobs[p][n]))
               Config_Name+=(str(smpl)+'.csv')
               try:
                with open(Config_Name) as csv_cache_file:
                  csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
                  for row in csv_reader_cache:
                      Weight.append(float(row[0]))
                      Length.append(float(row[1]))
                      if int(float(row[2]))<100000000:
                         Muon_w.append(float(row[2]))
                      if int(float(row[2]))==100000000:
                          FaultMuon_w.append(float(row[2]))
                csv_cache_file.close()
                for LMP in range (0,len(LL_Points)):
                    if ((HL_Jobs[p]==LL_RedPoint[LMP]) and (smpl==int(LL_Points[LMP][56]))):
                             LL_MetaPoints[LMP][57]=2
               except:
                IncompleteStatus=True
               for LMP in range (0,len(LL_Points)):
                 if ((HL_Jobs[p]==LL_RedPoint[LMP]) and (smpl==int(LL_Points[LMP][56]))):
                              LL_MetaPoints[LMP][58]+=1
           if IncompleteStatus==False:
              if len(Muon_w)==16:
                FitnessFunction=FCN(max(Weight), sum(Muon_w), 0)
              if  len(Muon_w)<16 and len(Muon_w)>0:
                FitnessFunction=FCN(min(Weight), sum(Muon_w)+((sum(Muon_w)/len(Muon_w))*len(FaultMuon_w)), 0)
              if len(Muon_w)==0:
                  FitnessFunction=100000000
              FCNPoint.append(FitnessFunction)
              X_new.append(FCNPoint)
           else:
               JobsForHL.append(HL_Meta_Jobs[p])
       Cash_output=open('/eos/experiment/ship/user/ffedship/EA_V2/Tasks_HL.csv',"w")
       Cash_writer = csv.writer(Cash_output)
       for op in range(0,len(JobsForHL)):
           Cash_writer.writerow(JobsForHL[op])
       Cash_output.close()
       Cash_output=open('/eos/experiment/ship/user/ffedship/EA_V2/Tasks_LL.csv',"w")
       Cash_writer = csv.writer(Cash_output)
       for op in range(0,len(LL_MetaPoints)):
           Cash_writer.writerow(LL_MetaPoints[op])
       Cash_output.close()
       RW.WriteCsvData(HLTasks,'UpdateLLTasks',0,0,LLTasks,_)
       Cash_output=open(EACache,"a")
       Cash_writer = csv.writer(Cash_output)
       for i in range(len(X_new)):
             Cash_writer.writerow(X_new[i])
       print UI.TimeStamp(), bcolors.OKGREEN+ str(len(X_new))+" points have been added to the cache file..."+bcolors.ENDC
#Writing New points into cache csv file
       Cash_output.close()
def CheckResult():
       HL_Meta_Jobs=RW.ReadCsvData(HLTasks,'ReadHLTasks',58)
       HL_Jobs=RW.ReadCsvData(HLTasks,'ReadHLTasks',56)
       LL_MetaPoints=RW.ReadCsvData(LLTasks,'ReadLLTasks',59)
       LL_Points=RW.ReadCsvData(LLTasks,'ReadLLTasks',57)
       LL_RedPoint=RW.ReadCsvData(LLTasks,'ReadLLTasks',56)
       JobsForHL=[]
       #We extract file names that we have to search for
       X_new=[]
       DeleteList=[]
       for p in range(0,len(HL_Jobs)):
           Length=[]
           Weight=[]
           Muon_w=[]
           FaultMuon_w=[]
           FitnessFunction=100000000
           IncompleteStatus=False
           for smpl in range (1,17):
               FCNPoint=[]
               Config_Name='/eos/experiment/ship/user/ffedship/EA_V2/Output/Config_'
               for n in range(0,56):
                  Config_Name+=(str(HL_Jobs[p][n])+'_')
                  FCNPoint.append(float(HL_Jobs[p][n]))
               Config_Name+=(str(smpl)+'.csv')
               try:
                with open(Config_Name) as csv_cache_file:
                  csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
                  for row in csv_reader_cache:
                      Weight.append(float(row[0]))
                      Length.append(float(row[1]))
                      if int(float(row[2]))<100000000:
                         Muon_w.append(float(row[2]))
                      if int(float(row[2]))==100000000:
                          FaultMuon_w.append(float(row[2]))
                csv_cache_file.close()
                for LMP in range (0,len(LL_Points)):
                    if ((HL_Jobs[p]==LL_RedPoint[LMP]) and (smpl==int(LL_Points[LMP][56]))):
                             LL_MetaPoints[LMP][57]=2
               except:
                IncompleteStatus=True
               for LMP in range (0,len(LL_Points)):
                 if ((HL_Jobs[p]==LL_RedPoint[LMP]) and (smpl==int(LL_Points[LMP][56]))):
                              LL_MetaPoints[LMP][58]+=1
           if IncompleteStatus==False:
              if len(Muon_w)==16:
                FitnessFunction=FCN(max(Weight), sum(Muon_w), 0)
              if  len(Muon_w)<16 and len(Muon_w)>0:
                FitnessFunction=FCN(min(Weight), sum(Muon_w)+((sum(Muon_w)/len(Muon_w))*len(FaultMuon_w)), 0)
              if len(Muon_w)==0:
                  FitnessFunction=100000000
              FCNPoint.append('Shield weight:')
              FCNPoint.append(max(Weight))
              FCNPoint.append('Weighted Muons:')
              FCNPoint.append(sum(Muon_w))
              FCNPoint.append('Fitness Function:')
              FCNPoint.append(FitnessFunction)
              X_new.append(FCNPoint)
           else:
               JobsForHL.append(HL_Meta_Jobs[p])
       Cash_output=open('/eos/experiment/ship/user/ffedship/EA_V2/Tasks_HL.csv',"w")
       Cash_writer = csv.writer(Cash_output)
       for op in range(0,len(JobsForHL)):
           Cash_writer.writerow(JobsForHL[op])
       Cash_output.close()
       Cash_output=open('/eos/experiment/ship/user/ffedship/EA_V2/Tasks_LL.csv',"w")
       Cash_writer = csv.writer(Cash_output)
       for op in range(0,len(LL_MetaPoints)):
           Cash_writer.writerow(LL_MetaPoints[op])
       Cash_output.close()
       RW.WriteCsvData(HLTasks,'UpdateLLTasks',0,0,LLTasks,_)
       Cash_output=open(RESULT,"w")
       Cash_writer = csv.writer(Cash_output)
       Cash_writer.writerow(['The point that was evaluated is:'])
       Cash_writer.writerow(X_new)
       print UI.TimeStamp(), bcolors.OKGREEN+ str(len(X_new))+" points have been added to the result file..."+bcolors.ENDC
#Writing New points into cache csv file
       Cash_output.close()
       if (len(X_new))>0:
           return True
       else:
           return False
def CheckCompletion(flocation,mode,g):
#Opening files
  CompletedPopulation=RW.ReadCsvData(EACache, 'ReadBareCache',1)
  RequiredPopulation=RW.ReadCsvData(flocation, mode,g)
#Here we want to tell user what fraction is done already
  Hit_Count=0
  for RP in RequiredPopulation:
        HitTrigger=False
        for CP in CompletedPopulation:
            if RP==CP:
               HitTrigger=True
        if HitTrigger==True:
           Hit_Count+=1
  if Hit_Count>=len(RequiredPopulation):
       print UI.TimeStamp(), bcolors.OKGREEN+"All points have been calculated, exiting now..."+bcolors.ENDC
       return True
  else:
        print UI.TimeStamp(), bcolors.OKGREEN+'Completed points: '+str((100*Hit_Count)/len(RequiredPopulation))+' %'+bcolors.ENDC
        return False
