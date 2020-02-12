################################################      Initialisation     #########################################################
##################################################################################################################################

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
print bcolors.HEADER+"--------------------------------------------------------------------------------------------------"
print "--------------------------------------------------------------------------------------------------"
print "------------------------            Checking Point Algorith              -------------------------"
print "--------------------------------------------------------------------------------------------------"
print "--------------------------------------------------------------------------------------------------" +bcolors.ENDC

#########I######################################   Importing libraries  ##########################################################
import random
import datetime
import time as t
import argparse
import copy
#Importing utility modules
import EA_HL_Utilities as EHU
import EA_HL_UI_Utilities as UI
import EA_HL_RW_Utilities as RW
import EA_OSI_Utilities as OSI

print UI.TimeStamp(), "Initialising Point FCN calculation algortithm..."
print UI.TimeStamp(), "Modules Have been imported successfully..."
print UI.TimeStamp(), "Loading cache file..."

###############################################    Parsing user settings   #######################################################
parser = argparse.ArgumentParser(description='Running mode')
parser.add_argument('--MODE',help="Please enter running mode: 'R' for reset and 'C' for continue", default='C')
parser.add_argument('--FSUB',help="Please enter Y/N if you want to force EA to submit point: ", default='N')
parser.add_argument('--WAIT',help="Please enter wait time in minutes: ", default='30')
parser.add_argument('--POINT',help="Please enter the point you want to evaluate: ", default='None')
parser.add_argument('--MSMPL',help="Choose Muon Sample: F/R", default='F')
DEFAULT_POINT = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
]
args = parser.parse_args()
Reset=args.MODE
Sample=args.MSMPL
if args.POINT=='None':
    point = DEFAULT_POINT
else:
    point= [int(e) if e.isdigit() else e for e in args.POINT.split(',')]
#############################################    Setting File locations     #####################################################
LLTasks='/eos/experiment/ship/user/ffedship/EA_V2/Tasks_LL.csv' #Low level tasks - csv with points for submission to Condor
HLTasks='/eos/experiment/ship/user/ffedship/EA_V2/Tasks_HL.csv' #Low level tasks - csv with points that have to be evaluated in the particular batch
RESULT='/eos/experiment/ship/user/ffedship/EA_V2/EA_Data_Log.csv'

##############################################    Default settings for EA   ######################################################
FSB=args.FSUB
TD=int(args.WAIT)*60
print UI.TimeStamp(), bcolors.OKBLUE+"Function Modules have loaded successfully "+bcolors.ENDC
print bcolors.HEADER+"--------------------------------------------------------------------------------------------------"
print "--------------------------------------------------------------------------------------------------" +bcolors.ENDC


#########################################     Starting new run     ###############################################################
##################################################################################################################################

#########################################     Initializing variables      ########################################################
_=0   #Dummy argument for some functions where fewer arguments are required

########################################     Determining initial status and generation    ########################################
if Reset=='R':
   points=[]
   points.append(EHU.Shrink(point))
   EHU.CleanUp('ALL')
   RW.WriteCsvData(HLTasks,'UpdateHLTasks',points,[],0,_)
   RW.WriteCsvData(HLTasks,'UpdateLLTasks',0,0,LLTasks,_)
   OSI.SubmitJobsCondor(FSB,Sample)
   if OSI.CheckResult():
      print 'Result is ready'
   else:
     print UI.TimeStamp(), 'Waiting for Condor response, going to sleep for ',TD/60, ' min...'
     t.sleep(TD)
if Reset=='C':
   OSI.SubmitJobsCondor(FSB,Sample)
   if OSI.CheckResult():
      print 'Result is ready'
   else:
     print UI.TimeStamp(), 'Waiting for Condor response, going to sleep for ',TD/60, ' min...'
     t.sleep(TD)
