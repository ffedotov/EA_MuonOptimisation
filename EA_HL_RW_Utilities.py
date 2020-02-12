#This file contains all utilities for csv write-read operations

########################################    Import libraries    #############################################
import csv
import copy
import EA_HL_Utilities as EHU

########################################     Main body functions    #########################################
def ReadCsvData(flocation,mode,g):
 veterans=[]
 veteran=[]
 if mode=='ReadBareCache':
  with open(flocation) as csv_cache_file:
    csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
    for row in csv_reader_cache:
      for i in range (0,56):
       veteran.append(int(float(row[i])))
      veterans.append(EHU.Shrink(veteran))
      veteran=[]
 if mode=='ReadFullCache':
  with open(flocation) as csv_cache_file:
    csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
    for row in csv_reader_cache:
      for i in range (0,57):
        veteran.append(int(float(row[i])))
      veterans.append(EHU.Shrink(veteran))
      veteran=[]
 if mode=='ReadIPO':
  csv_cache_file=open(flocation,"r")
  csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
  for row in csv_reader_cache:
    if int(row[43])==g:
      for i in range(0,42):
       veteran.append(float(row[i]))
      veterans.append(veteran)
      veteran=[]
  csv_cache_file.close()
  return veterans
 if mode=='LoadPop':
  csv_cache_file=open(flocation,"r")
  csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
  for row in csv_reader_cache:
    if int(row[42])==g:
      for i in range(0,42):
       veteran.append(float(row[i]))
      veterans.append(veteran)
      veteran=[]
  csv_cache_file.close()
  return veterans
 if mode=='GiveGeneration':
    with open(flocation) as csv_log_file:
     csv_reader_log = csv.reader(csv_log_file, delimiter=',')
     for row in csv_reader_log:
      Generation=int(row[43])
     csv_log_file.close()
    return Generation
 if mode =='ReadGen':
   with open(flocation) as csv_cache_file:
    csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
    for row in csv_reader_cache:
     if int(row[44])==g:
      for i in range (0,42):
       veteran.append(float(row[i]))
      veterans.append(veteran)
      veteran=[]
   csv_cache_file.close()
 if mode == 'ReadHLTasks':
  veterans=[]
  veteran=[]
  try:
   with open(flocation) as csv_cache_file:
     csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
     for row in csv_reader_cache:
      for i in range (0,g):
       veteran.append(int(float(row[i])))
      veterans.append(veteran)
      veteran=[]
   csv_cache_file.close()
   return veterans
  except:
   print "No High Level Tasks, File will be updated"
   return []
 if mode == 'ReadMultiHLTasks':
  veterans=[]
  veteran=[]
  for smpl in range (1,17):
    with open(flocation) as csv_cache_file:
     csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
     for row in csv_reader_cache:
      for i in range (0,g):
       veteran.append(int(float(row[i])))
      veteran.append(smpl)
      veterans.append(veteran)
      veteran=[]
    csv_cache_file.close()
  return veterans
 if mode =='ReadLLTasks':
  try:
   with open(flocation) as csv_cache_file:
    csv_reader_cache = csv.reader(csv_cache_file, delimiter=',')
    veterans=[]
    veteran=[]
    for row in csv_reader_cache:
      for i in range (0,g):
       veteran.append(int(float(row[i])))
      veterans.append(veteran)
      veteran=[]
   csv_cache_file.close()
  except:
   print "No Low Level Tasks, File will be updated"
   veterans=[]
   csv_cache_file.close()
 return veterans

def LogOperations(flocation,mode, message):
    if mode=='GetStatus':
         with open(flocation) as csv_log_file:
          csv_reader_log = csv.reader(csv_log_file, delimiter=',')
          for row in csv_reader_log:
           StatusCode=int(row[1])
         csv_log_file.close()
         return StatusCode
    if mode=='WriteLog':
        csv_writer_log=open(flocation,"a")
        log_writer = csv.writer(csv_writer_log)
        log_writer.writerow(message)
        csv_writer_log.close()
    if mode=='StartLog':
        csv_writer_log=open(flocation,"w")
        log_writer = csv.writer(csv_writer_log)
        log_writer.writerow(message)
        csv_writer_log.close()
    if mode =='StartDataLog':
          LogCodeString=[]
          csv_writer_log=open(flocation,"w")
          log_writer = csv.writer(csv_writer_log)
          LogCodeString.append('Time')
          LogCodeString.append('Generation')
          LogCodeString.append('Total population')
          LogCodeString.append('Population 1')
          LogCodeString.append('Population 2')
          LogCodeString.append('Best Fitness 1')
          LogCodeString.append('Best Fitness 2')
          LogCodeString.append('Best Fitness')
          log_writer.writerow(LogCodeString)
          csv_writer_log.close()

def WriteCsvData(flocation,mode,content1,content2,batchlimit,generation):
    Count=0
    Batch=0
    if mode=='WriteIPO':
     csv_writer_ipo=open(flocation,"w")
     ipo_writer = csv.writer(csv_writer_ipo)
     for i1 in content1:
      Count+=1
      if Count>batchlimit:
         Batch+=1
         Count=0
      i1c=copy.copy(i1)
      i1c.append(1)
      i1c.append(Batch)
      ipo_writer.writerow(i1c)
     for i2 in content2:
      Count+=1
      if Count>batchlimit:
        Batch+=1
        Count=0
      i2c=copy.copy(i2)
      i2c.append(2)
      i2c.append(Batch)
      ipo_writer.writerow(i2c)
     csv_writer_ipo.close()
    if mode=='UpdateIPO':
     csv_writer_ipo=open(flocation,"a")
     ipo_writer = csv.writer(csv_writer_ipo)
     for i1 in content1:
      Count+=1
      if Count>batchlimit:
         Batch+=1
         Count=0
      i1c=copy.copy(i1)
      i1c.append(1)
      i1c.append(Batch)
      ipo_writer.writerow(i1c)
     for i2 in content2:
      Count+=1
      if Count>batchlimit:
        Batch+=1
        Count=0
      i2c=copy.copy(i2)
      i2c.append(2)
      i2c.append(Batch)
      ipo_writer.writerow(i2c)
     csv_writer_ipo.close()
    if mode=='WriteGen':
       csv_writer_ipo=open(flocation,"w")
       ipo_writer = csv.writer(csv_writer_ipo)
       for i1 in content1:
         Count+=1
         if Count>batchlimit:
            Batch+=1
            Count=0
         i1c=copy.copy(i1)
         i1c.append(1)
         i1c.append(generation)
         i1c.append(Batch)
         ipo_writer.writerow(i1c)

       for i2 in content2:
         Count+=1
         if Count>batchlimit:
            Batch+=1
            Count=0
         i2c=copy.copy(i2)
         i2c.append(2)
         i2c.append(generation)
         i2c.append(Batch)
         ipo_writer.writerow(i2c)
       csv_writer_ipo.close()
    if mode=='UpdateHLTasks':
     try:
       #Stripping points that have been evaluated already
       FilteredPoints=[]
       for ind in content1:
           if EHU.CachingTest(content2, ind)==False:
               FilteredPoints.append(EHU.Expand(ind))
       OldPoints=ReadCsvData(flocation,'ReadHLTasks',58)
       OldRefPoints=ReadCsvData(flocation,'ReadHLTasks',56)
       while len(OldPoints)<len(FilteredPoints):
            for sp in range(0,len(FilteredPoints)):
                MatchFlag=False
                for op in range(0,len(OldRefPoints)):
                    if FilteredPoints[sp]==OldRefPoints[op]:
                        MatchFlag=True
                if MatchFlag==False:
                   Candidate=FilteredPoints[sp]
                   Candidate.append(0)
                   Candidate.append(0)
                   OldPoints.append(Candidate)
       Cash_output=open(flocation,"w")
       Cash_writer = csv.writer(Cash_output)
       for op in range(0,len(OldPoints)):
           Cash_writer.writerow(OldPoints[op])
       Cash_output.close()
     except:
      Cash_output=open(flocation,"w")
      Cash_writer = csv.writer(Cash_output)
      for sp in range(0,len(content1)):
          Candidate=content1[sp]
          Candidate.append(0)
          Candidate.append(0)
          Cash_writer.writerow(Candidate)
      Cash_output.close()
    if mode=='UpdateLLTasks':
     ExistingPoints=ReadCsvData(flocation,'ReadMultiHLTasks',56)
     ExistingPointsMeta=ReadCsvData(flocation,'ReadMultiHLTasks',56)
     for EPM in range(0,len(ExistingPointsMeta)):
        ExistingPointsMeta[EPM].append(0)
        ExistingPointsMeta[EPM].append(0)
     try:
      OldPoints=ReadCsvData(batchlimit,'ReadLLTasks',57)
      OldPointsMeta=ReadCsvData(batchlimit,'ReadLLTasks',59)
      for ep in range(0,len(ExistingPoints)):
           for op in range(0,len(OldPoints)):
                   if ExistingPoints[ep]==OldPoints[op]:
                       ExistingPointsMeta[ep][57]=OldPointsMeta[op][57]
                       ExistingPointsMeta[ep][58]=OldPointsMeta[op][58]

      Cash_output=open(batchlimit,"w")
      Cash_writer = csv.writer(Cash_output)
      for op in range(0,len(ExistingPointsMeta)):
          Cash_writer.writerow(ExistingPointsMeta[op])
      Cash_output.close()
     except:
       Cash_output=open(batchlimit,"w")
       Cash_writer = csv.writer(Cash_output)
       for op in range(0,len(ExistingPointsMeta)):
           Cash_writer.writerow(ExistingPointsMeta[op])
       Cash_output.close()







