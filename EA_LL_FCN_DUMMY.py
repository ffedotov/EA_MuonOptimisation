import time as t
import csv
import argparse
parser = argparse.ArgumentParser(description='Enter configuration settings for Dummy Evolutionary algorithm')
parser.add_argument('--mp', default='None')
args = parser.parse_args()
MP = [int(e) if e.isdigit() else e for e in args.mp.split(',')]
print "list", MP
def FitnessFunction(point,sample):
    XS_output=open(csv_output_name,"w")
    XS_write = csv.writer(XS_output)
    weight=0.0
    length = 0.0
    muons_w=0.0
    for p in point:
        weight=abs(8.0-float(p))
        length=abs(8.0-float(p))
        muons_w=abs(8.0-float(p))
    XS_write.writerow([weight, length, muons_w])
    XS_output.close()
if __name__ == '__main__':
    SubmissionPoint=[]
    Sample=0
    csv_output_name='/eos/experiment/ship/user/ffedship/EA_V2/Output/Config_'
    for sp in range (0,56):
        SubmissionPoint.append(MP[sp])
        csv_output_name+=(str(MP[sp])+'_')
    Sample=int(MP[56])
    csv_output_name+=(str(Sample)+'.csv')
    FitnessFunction(SubmissionPoint,Sample)


