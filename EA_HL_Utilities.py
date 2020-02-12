import EA_HL_UI_Utilities as UI
import EA_HL_RW_Utilities as RW
import random
import os, shutil
import subprocess
from itertools import repeat
from collections import Sequence
import csv


###### File locations ##############################
EACache='/eos/experiment/ship/user/ffedship/EA_V2/EA_Full_cache.csv'
EAIniPop='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_IPO.csv'
EAGen='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_GEN.csv'
LLTasks='/eos/experiment/ship/user/ffedship/EA_V2/Tasks_LL.csv'
HLTasks='/eos/experiment/ship/user/ffedship/EA_V2/Tasks_HL.csv'
LOG='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_Log.csv'
DATALOG='/eos/experiment/ship/user/ffedship/EA_V2/EA_HL_Data_Log.csv'
print UI.TimeStamp(), "Initialising EA High Level FCN calculation algortithm..."
print UI.TimeStamp(), "Modules Have been imported successfully..."


def StripFreeParams(point):
    fixed_params = []
    for low, high in FIXED_RANGES:
        fixed_params += point[low:high]
    return fixed_params

DEFAULT_POINT = [70,170,205,205,280,245,305,240,40,40,150,150,2,2,80,80,150,150,2,2,87,65,35,121,11,2,65,43,121,207,11,2,6,33,32,13,70,11,5,16,112,5,4,2,15,34,235,32,5,8,31,90,186,310,2,55,
]

MAX_BOUND_RAW = [
    305,
    305,
    305,
    305,
    305,
    305,
    305,
    305,
    100,
    100,
    200,
    200,
    70,
    70,
    100,
    100,
    200,
    200,
    70,
    70,
    100,
    100,
    200,
    200,
    70,
    70,
    100,
    100,
    200,
    200,
    70,
    70,
    100,
    100,
    200,
    200,
    70,
    70,
    100,
    100,
    200,
    200,
    70,
    70,
    100,
    100,
    200,
    200,
    70,
    70,
    100,
    100,
    200,
    200,
    70,
    70,
]

MIN_BOUND_RAW = [
    175,
    175,
    175,
    175,
    175,
    175,
    175,
    175,
    10,
    10,
    20,
    20,
    2,
    2,
    10,
    10,
    20,
    20,
    2,
    2,
    10,
    10,
    20,
    20,
    2,
    2,
    10,
    10,
    20,
    20,
    2,
    2,
    10,
    10,
    20,
    20,
    2,
    2,
    10,
    10,
    20,
    20,
    2,
    2,
    10,
    10,
    20,
    20,
    2,
    2,
    10,
    10,
    20,
    20,
    2,
    2,
]

FIXED_RANGES = [(0, 2), (8, 20)]

FIXED_PARAMS = StripFreeParams(DEFAULT_POINT)

def Shrink(point):
    stripped_point = []
    pos = 0
    for low, high in FIXED_RANGES:
        stripped_point += point[:low-pos]
        point = point[high-pos:]
        pos = high
    _, high = FIXED_RANGES[-1]
    stripped_point += point[high-pos:]
    return stripped_point

def CreateDiscreteSpace():
    dZgap = 10
    zGap = dZgap / 2  # halflengh of gap
    dimensions = 8 * [
        Integer(170 + zGap, 300 + zGap)  # magnet lengths
       ] + 8 * (
            2 * [
                Integer(10, 100)  # dXIn, dXOut
            ] + 2 * [
                Integer(20, 200)  # dYIn, dYOut
            ] + 2 * [
                Integer(2, 70)  # gapIn, gapOut
            ])
    return Space(StripFixedParams(dimensions))

def CreateReducedSpace(minimum, variation=0.1):
    dZgap = 10
    zGap = dZgap / 2  # halflengh of gap
    dimensions = 8 * [
        Integer(170 + zGap, 300 + zGap)  # magnet lengths
        ] + 8 * (
            2 * [
                Integer(10, 100)  # dXIn, dXOut
            ] + 2 * [
                Integer(20, 200)  # dYIn, dYOut
            ] + 2 * [
                Integer(2, 70)  # gapIn, gapOut
            ])
    reduced_dims = [Integer(max(int((1-variation)*m), dim.bounds[0]), min(int((1+variation)*m), dim.bounds[1])) for m, dim in zip(minimum, dimensions)]
    return Space(StripFixedParams(reduced_dims))

def Expand(point):
    _fixed_params = FIXED_PARAMS
    for low, high in FIXED_RANGES:
        point = point[0:low] + _fixed_params[:high-low] + point[low:]
        _fixed_params = _fixed_params[high-low:]
    return point

MIN_BOUND=Shrink(MIN_BOUND_RAW)

MAX_BOUND=Shrink(MAX_BOUND_RAW)

def GiveMinBound(ind):
    return MIN_BOUND[ind]

def GiveMaxBound(ind):
    return MAX_BOUND[ind]

def CachingTest(cache, individual):
    test_cache=[]
    test_ind=[]
    for c in range(0, len(cache)):
        test_cache_ind=[]
        for al in cache[c]:
            test_cache_ind.append(int(al))
        test_cache.append(test_cache_ind)
    for al in individual:
            test_ind.append(int(al))
    for cas in test_cache:
        if test_ind==cas:
           return True
    return False

def CreatePopulation(Size):
    population=[]
    for ind in range(0,Size):
        individual=[]
        for allelle in range(0,42):
            individual.append(random.randint(GiveMinBound(allelle),GiveMaxBound(allelle)))
        population.append(individual)

    return population

def CleanUp(M):
    if M=='ALL':
      subprocess.call(['condor_rm', '-all'])
      folder =  '/eos/experiment/ship/user/ffedship/EA_V2/Output'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      folder =  '/eos/experiment/ship/user/ffedship/EA_V2/Shared'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      folder =  '/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/MSG'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      folder =  '/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/SH'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      folder =  '/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/SUB'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      csv_writer_ipo=open(EAIniPop,"w")
      ipo_writer = csv.writer(csv_writer_ipo)
      csv_writer_ipo.close()
      csv_writer_gen=open(EAGen,"w")
      gen_writer = csv.writer(csv_writer_gen)
      csv_writer_gen.close()
      Cash_output=open(HLTasks,"w")
      Cash_writer = csv.writer(Cash_output)
      Cash_output.close()
      Cash_output=open(LLTasks,"w")
      Cash_writer = csv.writer(Cash_output)
      Cash_output.close()
      csv_writer_log=open(LOG,"w")
      log_writer = csv.writer(csv_writer_log)
      csv_data_log=open(DATALOG,"w")
      log_writer = csv.writer(csv_data_log)
      csv_data_log.close()
    if M=='SUB':
      subprocess.call(['condor_rm', '-all'])
      folder =  '/eos/experiment/ship/user/ffedship/EA_V2/Output'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      folder =  '/eos/experiment/ship/user/ffedship/EA_V2/Shared'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      folder =  '/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/MSG'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      folder =  '/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/SH'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e
      folder =  '/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/SUB'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print e

def mutRsGaussianInt(individual, sigma, indpb):
    """This function applies a gaussian mutation of mean *mu* and standard
    deviation *sigma* on the input individual. This mutation expects a
    :term:`sequence` individual composed of real valued attributes.
    The *indpb* argument is the probability of each attribute to be mutated.

    :param individual: Individual to be mutated.
    :param mu: Mean or :term:`python:sequence` of means for the
               gaussian addition mutation.
    :param sigma: Standard deviation or :term:`python:sequence` of
                  standard deviations for the gaussian addition mutation.
    :param indpb: Independent probability for each attribute to be mutated.
    :returns: A tuple of one individual.

    This function uses the :func:`~random.random` and :func:`~random.gauss`
    functions from the python base :mod:`random` module.
    """
    size = len(individual)
    if not isinstance(sigma, Sequence):
        sigma = repeat(sigma, size)

    elif len(sigma) < size:
        raise IndexError("sigma must be at least the size of individual: %d < %d" % (len(sigma), size))
    for i, s in zip(xrange(size), sigma):
        if random.random() < indpb:
            sign=random.choice((-1,1))
            scale=(GiveMaxBound(i)-GiveMinBound(i))/10

            individual[i] += sign*(int(random.gauss(float(scale), s)))
            if individual[i]>GiveMaxBound(i):
              individual[i]=GiveMaxBound(i)
            if individual[i]<GiveMinBound(i):
              individual[i]=GiveMinBound(i)
    return individual,

def FitnessEvaluation(individual):
  CachedPopulation=RW.ReadCsvData(EACache, 'ReadBareCache',0)
  CachedUtility=RW.ReadCsvData(EACache, 'ReadFullCache',0)
#Here we want to tell user what fraction is done already
  for CP in range(0,len(CachedPopulation)):
      if individual==CachedPopulation[CP]:
          if CachedUtility[CP][42]>=0:
           return CachedUtility[CP][42],
          else:
           return 1000000.0,
  return []

def initIndividual(icls, content):
    return icls(content)

def RetrievePopulation1(pcls, ind_init):
 Population1=RW.ReadCsvData(EAIniPop,'LoadPop',1)
 return pcls(ind_init(c) for c in Population1)

def RetrievePopulation2(pcls, ind_init):
 Population2=RW.ReadCsvData(EAIniPop,'LoadPop',2)
 return pcls(ind_init(c) for c in Population2)

def RetrieveGeneration1(pcls, ind_init):
 Population1=RW.ReadCsvData(EAGen,'LoadPop',1)
 return pcls(ind_init(c) for c in Population1)

def RetrieveGeneration2(pcls, ind_init):
 Population2=RW.ReadCsvData(EAGen,'LoadPop',2)
 return pcls(ind_init(c) for c in Population2)
