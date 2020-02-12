################################################      Info              #########################################################
#This is the main script that runs Optimization of the Muon Shield by using Evolutionary Algorithm
# Author - Filips Fedotovs - PhD Student at UCL

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
print "------------------------ Evolutionary Algorithm Muon shield optimization -------------------------"
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
#Import EA DEAP library
import deap
from deap import creator, base, tools, algorithms
print UI.TimeStamp(), "Initialising EA High Level FCN calculation algortithm..."
print UI.TimeStamp(), "Modules Have been imported successfully..."
print UI.TimeStamp(), "Loading cache file..."

###############################################    Parsing user settings   #######################################################
parser = argparse.ArgumentParser(description='Running mode')
parser.add_argument('--MODE',help="Please enter running mode: 'R' for reset and 'C' for continue", default='C')
parser.add_argument('--IPO',help="Please enter initial size population for each island: ", default='200')
parser.add_argument('--FSUB',help="Please enter Y/N if you want to force EA to submit point: ", default='N')
parser.add_argument('--BATCH',help="Please enter submission batch size: ", default='100')
parser.add_argument('--WAIT',help="Please enter wait time in minutes: ", default='30')
args = parser.parse_args()
Reset=args.MODE
toolbox = base.Toolbox()
toolbox.register("migrate", tools.migRing)

#############################################    Setting File locations     #####################################################
EACache='/eos/experiment/ship/user/ffedship/EA_V2/EA_Full_cache.csv' #Thats where points are cached
EAIniPop='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_IPO.csv'  #Thats is where population is kept
EAGen='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_GEN.csv'  #Current generation points
LLTasks='/eos/experiment/ship/user/ffedship/EA_V2/Tasks_LL.csv' #Low level tasks - csv with points for submission to Condor
HLTasks='/eos/experiment/ship/user/ffedship/EA_V2/Tasks_HL.csv' #Low level tasks - csv with points that have to be evaluated in the particular batch
LOG='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_Log.csv'
DATALOG='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_Data_Log.csv'

##############################################    Default settings for EA   ######################################################
IPO=int(args.IPO) ###Initial population size (by default is parsed from command line by using --IPO
BTCH=int(args.BATCH)
#Maximum points per batch (this is done because there is a technical limitation for submitting all points at once, 100 is the maximum)
#Also please note ,that this code is limited to 4 batch submissions,
# hence the maximum population per each island cannot exceed 200, however it is possible to change it on demand
FSB=args.FSUB
TD=int(args.WAIT)*60
#Select sampling proportion in range from  0.1 to 1.0
SMPL=0.25
SML=int(float(IPO)*SMPL)
#Select crossing probability in range from  0.1 to 1.0
CXPB=0.5
CXX='CUP'
#Select Mutation Mode - Based on Hyper Tuning studies we consider Gaussian Method
MUTPB=0.7
#####Mutation probaility is set at 0.7
sigma=0.2
MIGPB=0.2
if CXX=='C1P': #Recombination happens by splitting DNA code of parents in two parts each and exchanging them
   toolbox.register("mate", tools.cxOnePoint)
if CXX=='C2P': #Recombination happens by splitting DNA code of parents in three parts each and exchanging them
   toolbox.register("mate", tools.cxTwoPoint)
if CXX=='CUP': #Unigorm blending
   toolbox.register("mate", tools.cxUniform)
toolbox.register("evaluate", EHU.FitnessEvaluation) #This tool evaluates population using function evalOneMax()
print UI.TimeStamp(), bcolors.OKBLUE+"Function Modules have loaded successfully "+bcolors.ENDC
print bcolors.HEADER+"--------------------------------------------------------------------------------------------------"
print "--------------------------------------------------------------------------------------------------" +bcolors.ENDC

##########################################     Loading Cache   ###################################################################
print UI.TimeStamp(), "Loading cache..."
CACHE=RW.ReadCsvData(EACache, 'ReadFullCache',0)
CUT_CACHE=RW.ReadCsvData(EACache, 'ReadBareCache',0)
print UI.TimeStamp(), "Checking the log files..."

#########################################     Starting new run     ###############################################################
##################################################################################################################################

#########################################     Initializing variables      ########################################################
StatusCode=0 # Helps tracking the phase of the algorithm
LogCodeString=[] # String to write data log
BestFitness1=1000000.0    # Default Fitness values
BestFitness2=1000000.0    # Default Fitness values
PopulationSize1=IPO       # Initial population sizes
PopulationSize2=IPO
PopulationSize=PopulationSize1+PopulationSize2 # Total population size
BestFitness=min(BestFitness1,BestFitness2)    # Best fitness
_=0   #Dummy argument for some functions where fewer arguments are required

########################################     Determining initial status and generation    ########################################
try:   # Trying to read file to see whether the program has been ran earlier
 if Reset=='C':
    StatusCode=RW.LogOperations(LOG,'GetStatus',0)   # Setting status code to the latest finished phase
    print UI.TimeStamp(), "The log file has been created at previous run, current status is "+ str(StatusCode)
 else:
   print UI.TimeStamp(), "Resetting, starting process from the scratch"
   EHU.CleanUp('ALL')
   RW.LogOperations(LOG,'WriteLog',StatusCodeString)
   print UI.TimeStamp(), "The log has been created, beginning the optimization run"
except:
  print UI.TimeStamp(), "No log detected, starting the new one..."
  EHU.CleanUp('ALL')
  StatusCodeString=[UI.TimeStamp(),str(0),'Starting new run']
  RW.LogOperations(LOG,'StartLog',StatusCodeString)
  print UI.TimeStamp(), "The log has been created, beginning the optimization run"
try:
    Generation=RW.ReadCsvData(EAGen,'GiveGeneration',0)
    print UI.TimeStamp(), "Current generation is "+str(Generation)
except:
  Generation=0
if Generation==0:
   RW.LogOperations(DATALOG,'StartDataLog',0)

# The function bellow helps to automate batch submission cycles
def StatusCodeCycle(StatusCode):
    if StatusCode>=1 and StatusCode<=4:
        return(0)
    if StatusCode>=5 and StatusCode<=8:
        return(1)
    if StatusCode>=9 and StatusCode<=12:
        return(2)
    if StatusCode>=13 and StatusCode<=16:
        return(3)
    if StatusCode>=18 and StatusCode<=21:
        return(0)
    if StatusCode>=22 and StatusCode<=25:
        return(1)
    if StatusCode>=25 and StatusCode<=29:
        return(2)
    if StatusCode>=30 and StatusCode<=33:
        return(3)

#####################################      Starting Population initialization      ######################################################
if StatusCode==0:
 InitialPopulation1=EHU.CreatePopulation(IPO)  # Generating random points for Island 1
 InitialPopulation2=EHU.CreatePopulation(IPO)  # Generating random points for Island 2
 print UI.TimeStamp(), "The random population for Island-1 and Island-2 has been generated, writing them into Initial Population file."
 RW.WriteCsvData(EAIniPop,'WriteIPO',InitialPopulation1,InitialPopulation2,BTCH,_)  #   Writing them into csv file
 StatusCodeString=[UI.TimeStamp(),str(1),'Files with initial population have been generated']  #    Preparing string for log
 RW.LogOperations(LOG,'WriteLog',StatusCodeString) #############Writing into log
 StatusCode=1    #Changing status
 print UI.TimeStamp(), 'Files with initial population have been generated'  #  Message for the user

#####################################     The cycle below evaluates initial population    ###############################################
#########################################################################################################################################
while (StatusCode<17 and StatusCode>0):
 period=StatusCodeCycle(StatusCode)
 if StatusCode==((4*period)+1):
    Population=RW.ReadCsvData(EAIniPop,'ReadIPO',period)
    ExtPopulation=[]
    for ind in Population:
        ExtInd=EHU.Expand(copy.copy(ind))
        if EHU.CachingTest(CACHE, ExtInd)==False:
            ExtPopulation.append(EHU.Shrink(ExtInd))
    RW.WriteCsvData(HLTasks,'UpdateHLTasks',ExtPopulation,CUT_CACHE,period,_)
    StatusCodeString=[UI.TimeStamp(),str(StatusCode+1),'High Level tasks for Batch ',period,' have been generated...']
    RW.LogOperations(LOG,'WriteLog',StatusCodeString)
    StatusCode+=1
    print UI.TimeStamp(), 'High Level tasks for Batch ',period,' have been generated...'
#Status 2: Updating Low Level Tasks for Batch 1
 if StatusCode==((4*period)+2):
   RW.WriteCsvData(HLTasks,'UpdateLLTasks',0,0,LLTasks,_)
   StatusCodeString=[UI.TimeStamp(),str(StatusCode+1),'Low level tasks for Batch ',period,' have been updated']
   RW.LogOperations(LOG,'WriteLog',StatusCodeString)
   StatusCode+=1
 print UI.TimeStamp(), 'Low level tasks for Batch ',period,' have been updated'
#Status 3: Submitting jobs for Island 1, Batch 1 to condor
 if StatusCode==((4*period)+3):
  print UI.TimeStamp(),'Sending Batch ',period,' to the Condor'
  OSI.SubmitJobsCondor(FSB,'R')
  StatusCodeString=[UI.TimeStamp(),str(StatusCode+1),'Initial population points for batch ',period,' have been sent to Condor for evaluation']
  RW.LogOperations(LOG,'WriteLog',StatusCodeString)
  StatusCode+=1
  print UI.TimeStamp(), 'Initial population points for Batch ',period,' have been sent to Condor for evaluation'
#Status 4 - Checking for Condor jobs
 if StatusCode==((4*period)+4):
    for cycle in range(0,6):
        OSI.CheckResults()
        if OSI.CheckCompletion(EAIniPop,'ReadIPO',period)==False:
            OSI.SubmitJobsCondor(FSB,'R')
            print UI.TimeStamp(), 'Waiting for Condor response, going to sleep for ',TD/60, ' min...'
            t.sleep(TD)
        else:
            StatusCodeString=[UI.TimeStamp(),str(StatusCode+1),'Initial population points for Batch ',period,' have been evaluated']
            RW.LogOperations(LOG,'WriteLog',StatusCodeString)
            EHU.CleanUp('SUB')
            StatusCode+=1
            break

#########################################        Sampling, crossing and mutating     ####################################################
if StatusCode==17:
    Generation+=1
    creator.create("Fitness", base.Fitness, weights=(-1.0,)) #We define the weighting of Fitness reference values: negative value indicates that the best fitness is the smallest one
    creator.create("individual", list, fitness=creator.Fitness)
    toolbox.register("Individual", EHU.initIndividual, creator.individual) #Specifying length of the DNA for each individual
    toolbox.register("Population1", EHU.RetrievePopulation1, list, toolbox.Individual)
    toolbox.register("Population2", EHU.RetrievePopulation2, list, toolbox.Individual)
    pop1 = toolbox.Population1()
    pop2 = toolbox.Population2()
    print pop1
    print pop2
    PopulationSize1=len(pop1)
    PopulationSize2=len(pop2)
    PopulationSize=PopulationSize1+PopulationSize2
    fitnesses1 = list(map(toolbox.evaluate, pop1))
    for ind1, fit1 in zip(pop1, fitnesses1):
          ind1.fitness.values = fit1
          if BestFitness1>fit1[0]:
              BestFitness1=fit1[0]
    fitnesses2 = list(map(toolbox.evaluate, pop2))
    for ind2, fit2 in zip(pop2, fitnesses2):
          ind2.fitness.values = fit2
          if BestFitness2>fit2[0]:
              BestFitness2=fit2[0]
    BestFitness=min(BestFitness1,BestFitness2)
    LogCodeString=[UI.TimeStamp(),Generation,PopulationSize,PopulationSize1,PopulationSize2,BestFitness1,BestFitness2,BestFitness]
    RW.LogOperations(DATALOG,'WriteLog',LogCodeString)
    print UI.TimeStamp(), "Run data has been recorded in the csv file"
    if random.random() < MIGPB:
       populations = [pop1,pop2]
       toolbox.migrate(populations,int(float(IPO)*0.05),tools.selBest)
    Temp_pop1 = list(map(toolbox.clone, pop1))
    Temp_pop2 = list(map(toolbox.clone, pop2))
    Temp_pop1=tools.selBest(Temp_pop1, SML, fit_attr='fitness')
    Temp_pop2=tools.selBest(Temp_pop2, SML, fit_attr='fitness')
    for child1, child2 in zip(Temp_pop1[::2], Temp_pop1[1::2]): #Mating selected candidates
           if CXX=='CUP': #Unigorm blending
              toolbox.mate(child1, child2, CXPB)
           else:
             if random.random() < CXPB:  #Mating happens with probability
               toolbox.mate(child1, child2)
    for child1, child2 in zip(Temp_pop2[::2], Temp_pop2[1::2]): #Mating selected candidates
           if CXX=='CUP': #Unigorm blending
              toolbox.mate(child1, child2, CXPB)
           else:
             if random.random() < CXPB:  #Mating happens with probability
               toolbox.mate(child1, child2)
    for mutant1 in Temp_pop1: #Mutating based on settings
        EHU.mutRsGaussianInt(mutant1, sigma, MUTPB)
    for mutant2 in Temp_pop2: #Mutating based on settings
        EHU.mutRsGaussianInt(mutant2, sigma, MUTPB)
    RW.WriteCsvData(EAGen,'WriteGen',Temp_pop1,Temp_pop2,BTCH,Generation)
    StatusCodeString=[UI.TimeStamp(),str(18),'File with current population generation ',Generation,' has been generated']
    RW.LogOperations(LOG,'WriteLog',StatusCodeString)
    StatusCode=18
    print UI.TimeStamp(), 'Files with current generation ',Generation, 'have been generated'


#####################################     The cycle below evaluates generations      ####################################################
#########################################################################################################################################
for c in range(0,1):

 ####################################      The cycle below evaluates current generation     ############################################
 while (StatusCode>17 and StatusCode<34):
  period=StatusCodeCycle(StatusCode)
  print 'StatusCode is',StatusCode,'period',period
  if StatusCode==(4*period)+18:
    Population1=RW.ReadCsvData(EAGen,'ReadGen',period)
    RW.WriteCsvData(HLTasks,'UpdateHLTasks',Population1,CUT_CACHE,period,_)
    StatusCodeString=[UI.TimeStamp(),str(StatusCode+1),'High Level tasks for batch ',period,' have been generated...']
    RW.LogOperations(LOG,'WriteLog',StatusCodeString)
    StatusCode+=1
    print UI.TimeStamp(), 'High Level tasks for batch ',period,' have been generated...'
  if StatusCode==(4*period)+19:
    print UI.TimeStamp(),'Updating low level tasks'
    RW.WriteCsvData(HLTasks,'UpdateLLTasks',0,0,LLTasks,_)
    StatusCodeString=[UI.TimeStamp(),str(StatusCode+1),'Low level tasks for batch ',period,' have been updated']
    RW.LogOperations(LOG,'WriteLog',StatusCodeString)
    StatusCode+=1
    print UI.TimeStamp(), 'Low level tasks for batch ',period,' have been updated'
  if StatusCode==(4*period)+20:
   print UI.TimeStamp(),'Sending jobs for batch ',period,' to the Condor'
   OSI.SubmitJobsCondor(FSB,'R')
   StatusCodeString=[UI.TimeStamp(),str(StatusCode+1),'Current generation points for batch '+str(period)+' have been sent to Condor for evaluation']
   RW.LogOperations(LOG,'WriteLog',StatusCodeString)
   StatusCode+=1
   print UI.TimeStamp(), 'Current population points for batch '+str(period)+' have been sent to Condor for evaluation'
  if StatusCode==(4*period)+21:
    for cycle in range(0,15):
        OSI.CheckResults()
        if OSI.CheckCompletion(EAGen,'ReadGen',period)==False:
            OSI.SubmitJobsCondor(FSB,'R')
            print UI.TimeStamp(), 'Waiting for Condor response, going to sleep for '+str(TD/60)+' min...'
            t.sleep(TD)
            continue
        else:
            StatusCodeString=[UI.TimeStamp(),str(StatusCode+1),'Generational population points for batch' + str(period)+' have been evaluated']
            RW.LogOperations(LOG,'WriteLog',StatusCodeString)
            EHU.CleanUp('SUB')
            StatusCode+=1
            break

#########################################        Sampling, crossing and mutating     ####################################################
 if StatusCode==34:
  creator.create("Fitness", base.Fitness, weights=(-1.0,)) #We define the weighting of Fitness reference values: negative value indicates that the best fitness is the smallest one
  creator.create("individual", list, fitness=creator.Fitness)
  toolbox.register("Individual", EHU.initIndividual, creator.individual) #Specifying length of the DNA for each individual
  toolbox.register("Population1", EHU.RetrieveGeneration1, list, toolbox.Individual)
  toolbox.register("Population2", EHU.RetrieveGeneration2, list, toolbox.Individual)
  CurrentPopulation1 = toolbox.Population1()
  CurrentPopulation2 = toolbox.Population2()
  RW.WriteCsvData(EAIniPop,'UpdateIPO',CurrentPopulation1,CurrentPopulation2,BTCH,_)
  print UI.TimeStamp(), "The current population 2 has been recorded in the csv file"
  StatusCodeString=[UI.TimeStamp(),str(35),'Current generation'+ str(Generation)+ ' has been added to IPO file.']
  RW.LogOperations(LOG,'WriteLog',StatusCodeString)
  StatusCode=35
  print UI.TimeStamp(), 'Evaluated generation '+ str(Generation)+ ' has been added to the file'
 if StatusCode==35:
    Generation+=1
    creator.create("Fitness", base.Fitness, weights=(-1.0,)) #We define the weighting of Fitness reference values: negative value indicates that the best fitness is the smallest one
    creator.create("individual", list, fitness=creator.Fitness)
    toolbox.register("Individual", EHU.initIndividual, creator.individual) #Specifying length of the DNA for each individual
    toolbox.register("Population1", EHU.RetrievePopulation1, list, toolbox.Individual)
    toolbox.register("Population2", EHU.RetrievePopulation2, list, toolbox.Individual)
    pop1 = toolbox.Population1()
    pop2 = toolbox.Population2()
    PopulationSize1=len(pop1)
    PopulationSize2=len(pop2)
    PopulationSize=PopulationSize1+PopulationSize2
    fitnesses1 = list(map(toolbox.evaluate, pop1))
    for ind1, fit1 in zip(pop1, fitnesses1):
          ind1.fitness.values = fit1
          if BestFitness1>fit1[0]:
              BestFitness1=fit1[0]
    fitnesses2 = list(map(toolbox.evaluate, pop2))
    for ind2, fit2 in zip(pop2, fitnesses2):
          ind2.fitness.values = fit2
          if BestFitness2>fit2[0]:
              BestFitness2=fit2[0]
    BestFitness=min(BestFitness1,BestFitness2)
    LogCodeString=[UI.TimeStamp(),Generation,PopulationSize,PopulationSize1,PopulationSize2,BestFitness1,BestFitness2,BestFitness]
    RW.LogOperations(DATALOG,'WriteLog',LogCodeString)
    print UI.TimeStamp(), "Run data has been recorded in the csv file"
    if random.random() < MIGPB:
       populations = [pop1,pop2]
       toolbox.migrate(populations,int(float(IPO)*0.05),tools.selBest)
    Temp_pop1 = list(map(toolbox.clone, pop1))
    Temp_pop2 = list(map(toolbox.clone, pop2))
    Temp_pop1=tools.selBest(Temp_pop1, SML, fit_attr='fitness')
    Temp_pop2=tools.selBest(Temp_pop2, SML, fit_attr='fitness')
    for child1, child2 in zip(Temp_pop1[::2], Temp_pop1[1::2]): #Mating selected candidates
           if CXX=='CUP': #Unigorm blending
              toolbox.mate(child1, child2, CXPB)
           else:
             if random.random() < CXPB:  #Mating happens with probability
               toolbox.mate(child1, child2)

    for child1, child2 in zip(Temp_pop2[::2], Temp_pop2[1::2]): #Mating selected candidates
           if CXX=='CUP': #Unigorm blending
              toolbox.mate(child1, child2, CXPB)
           else:
             if random.random() < CXPB:  #Mating happens with probability
               toolbox.mate(child1, child2)
    for mutant1 in Temp_pop1: #Mutating based on settings
        EHU.mutRsGaussianInt(mutant1, sigma, MUTPB)
    for mutant2 in Temp_pop2: #Mutating based on settings
        EHU.mutRsGaussianInt(mutant2, sigma, MUTPB)
    RW.WriteCsvData(EAGen,'WriteGen',Temp_pop1,Temp_pop2,BTCH,Generation)
    StatusCodeString=[UI.TimeStamp(),str(18),'Files with current population generation '+str(Generation)+' have been generated']
    RW.LogOperations(LOG,'WriteLog',StatusCodeString)
    StatusCode=18
    print UI.TimeStamp(), 'Files with current generation '+str(Generation)+' have been generated'
