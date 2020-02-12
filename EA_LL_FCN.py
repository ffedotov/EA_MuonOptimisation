import ROOT as r
import os
import copy
import config
import subprocess
import shutil
import base64
import shipunit as u
import filelock
import geomGeant4
import time as t
import csv
import argparse
from ShipGeoConfig import ConfigRegistry
import shipDet_conf
import numpy as np
from analyse import analyse
from common import generate_geo
from disney_common import create_id, ParseParams,FCN
parser = argparse.ArgumentParser(description='Enter configuration settings for Evolutionary algorithm')
parser.add_argument('--mp', default='None')
args = parser.parse_args()
MP = [int(e) if e.isdigit() else e for e in args.mp.split(',')]

print "list", MP
def generate(
        inputFile,
        paramFile,
        outFile,
        seed=1,
        nEvents=None
):

    firstEvent = 0
    dy = 10.
    vessel_design = 5
    shield_design = 8
    mcEngine = 'TGeant4'
    sameSeed = seed
    theSeed = 1
    phiRandom = False  # only relevant for muon background generator
    followMuon = True  # only transport muons for a fast muon only background
    print ('FairShip setup to produce', nEvents, 'events')
    r.gRandom.SetSeed(theSeed)
    ship_geo = ConfigRegistry.loadpy(
        '$FAIRSHIP/geometry/geometry_config.py',
        Yheight=dy,
        tankDesign=vessel_design,
        muShieldDesign=shield_design,
        muShieldGeo=paramFile)
    run = r.FairRunSim()
    run.SetName(mcEngine)  # Transport engine
    run.SetOutputFile(outFile)  # Output file
    # user configuration file default g4Config.C
    run.SetUserConfig('g4Config.C')
    modules = shipDet_conf.configure(run, ship_geo)
    primGen = r.FairPrimaryGenerator()
    primGen.SetTarget(ship_geo.target.z0 + 50 * u.m, 0.)
    MuonBackgen = r.MuonBackGenerator()
    MuonBackgen.Init(inputFile, firstEvent, phiRandom)
    MuonBackgen.SetSmearBeam(3 * u.cm)  # beam size mimicking spiral
    if sameSeed:
        MuonBackgen.SetSameSeed(sameSeed)
    primGen.AddGenerator(MuonBackgen)
    nEvents = MuonBackgen.GetNevents()-1
    print ('Process ', nEvents, ' from input file, with Phi random=', phiRandom)
    if followMuon:
        modules['Veto'].SetFastMuon()
    run.SetGenerator(primGen)
    run.SetStoreTraj(r.kFALSE)
    run.Init()
    print ('Initialised run.')
    geomGeant4.addVMCFields(ship_geo, '', True)
    print ('Start run of {} events.'.format(nEvents))
    run.Run(nEvents)
    print ('Finished simulation of {} events.'.format(nEvents))

def FitnessFunction(point,sample):
  try:
    tmpl = copy.deepcopy(config.RESULTS_TEMPLATE)
    params=point

    paramFile = '/eos/experiment/ship/user/ffedship/EA_V2/Shared/params'+str(sample)+'_{}.root'.format(
        create_id(params)
    )
    geoinfoFile = paramFile.replace('params', 'geoinfo')
    heavy = '/eos/experiment/ship/user/ffedship/EA_V2/Shared/heavy'+str(sample)+'_{}'.format(create_id(params))
    lockfile = paramFile + '.lock'
    print heavy,lockfile
    if os.path.exists(geoinfoFile):
        geolockfile = geoinfoFile + '.lock'
        lock = filelock.FileLock(geolockfile)
        if not lock.is_locked:
            with lock:
                with open(geoinfoFile, 'r') as f:
                    length, weight = map(float, f.read().strip().split(','))
                tmpl['weight'] = weight
                tmpl['length'] = length
    while not os.path.exists(paramFile) and not os.path.exists(heavy):
        lock = filelock.FileLock(lockfile)
        if not lock.is_locked:
            with lock:
                tmpl['status'] = 'Acquired lock.'
                tmp_paramFile = generate_geo(
                    paramFile.replace('.r', '.tmp.r'),
                    params
                )
                subprocess.call(
                    [
                        'python2',
                        '/afs/cern.ch/user/f/ffedship/private/EA_Muon_Shield_V2/get_geo.py',
                        '-g', tmp_paramFile,
                        '-o', geoinfoFile
                        ])

                shutil.move(
                    '/eos/experiment/ship/user/ffedship/EA_V2/Shared/' + os.path.basename(tmp_paramFile),
                    paramFile.replace(
                        'shared', 'output'
                    ).replace(
                        'params', 'geo'
                    )
                )
                with open(geoinfoFile, 'r') as f:
                    length, weight = map(float, f.read().strip().split(','))
                tmpl['weight'] = weight
                tmpl['length'] = length
                shutil.move('/eos/experiment/ship/user/ffedship/EA_V2/Geometry/' + os.path.basename(tmp_paramFile), paramFile)

                tmpl['status'] = 'Created geometry.'
                print "Fitness Function Message: Geometry has been generated using config ", point
                print "Fitness Function Message: Length ", length
                print "Fitness Function Message: Weight ", weight
        else:
            sleep(60)
    outFile = root_output_name

    tmpl['status'] = 'Simulating...'
    generate(
         inputFile=root_input_name,
         paramFile=paramFile,
         outFile=root_output_name,
         seed=1,
         nEvents=10000
            )

    tmpl['status'] = 'Analysing...'
    chain = r.TChain('cbmsim')
    chain.Add(outFile)
    xs = analyse(chain, 'hists.root')
    tmpl['muons'] = len(xs)
    tmpl['muons_w'] = sum(xs)
    print "muons: ", tmpl['muons']
    print "muons_w: ", tmpl['muons_w']
    print "Fitness", FCN(tmpl['weight'], np.array(xs), tmpl['length'])[0]
    XS_output=open(csv_output_name,"w")
    XS_write = csv.writer(XS_output)
    XS_write.writerow([tmpl['weight'], tmpl['length'], tmpl['muons_w']])
    XS_output.close()
    tmpl['error'] = None
    tmpl['status'] = 'Done.'
    os.remove(root_output_name)
  except:
    print "EA_LL_FCN Message: Wrong geometry, operation rejected, negative values assigned"
    XS_output=open(csv_output_name,"w")
    XS_write = csv.writer(XS_output)
    XS_write.writerow([100000000, 10000000, 100000000])
    XS_output.close()
if __name__ == '__main__':
    r.gErrorIgnoreLevel = r.kWarning
    r.gSystem.Load('libpythia8')
    SubmissionPoint=[]
    Sample=0
    csv_output_name='/eos/experiment/ship/user/ffedship/EA_V2/Output/Config_'
 #   root_output_name='/eos/experiment/ship/user/ffedship/EA/output/SimOut_'
    
    root_output_name='SimOut_'
    for sp in range (0,56):
        SubmissionPoint.append(MP[sp])
        csv_output_name+=(str(MP[sp])+'_')
        root_output_name+=(str(MP[sp])+'_')


    Sample=int(MP[56])
    csv_output_name+=(str(Sample)+'.csv')
    root_output_name+=(str(Sample)+'.root')
    print "root_output", root_output_name
    print "csv_output", csv_output_name
    print "Sample", Sample
    root_input_name='root://eospublic.cern.ch//eos/experiment/ship/user/ffedship/EA_V2/Reduced_Sample/reduced_muons_'+str(Sample)+'_16.root'
    print "root_input_name" , root_input_name
    FitnessFunction(SubmissionPoint,Sample)


