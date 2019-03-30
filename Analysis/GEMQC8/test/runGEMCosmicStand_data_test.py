# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options: SingleMuPt100_cfi -s GEN,SIM,DIGI,L1,DIGI2RAW,RAW2DIGI,L1Reco,RECO --conditions auto:run2_mc --magField 38T_PostLS1 --datatier GEN-SIM --geometry GEMCosmicStand --eventcontent FEVTDEBUGHLT --era phase2_muon -n 100 --fileout out_reco.root
import datetime
print datetime.datetime.now()
import FWCore.ParameterSet.Config as cms
import configureRun_cfi as runConfig

# options
import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing('analysis')

options.register("runNum",1,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Run number")

options.register("eventsPerJob",1000,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "The number of events (in each file)")

options.register("idxJob","-1",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "The index of this root file")
options.register('mps',
                 '',
                 VarParsing.VarParsing.multiplicity.list,
                 VarParsing.VarParsing.varType.int,
                 "List of MPs to process")


options.parseArguments()

# The superchambers in the 15 slots
SuperChType = runConfig.StandConfiguration

print(SuperChType)

# Calculation of SuperChSeedingLayers from SuperChType
SuperChSeedingLayers = []

for i in range (0,30):
  SuperChSeedingLayers.append(0)

for j in range (0,3):
  for i in range (5*j,5*(j+1)):
    if (SuperChType[i]!='0'):
      SuperChSeedingLayers[i*2]=1
      SuperChSeedingLayers[i*2+1]=3
      break
  for i in range (5*(j+1)-1,5*j-1,-1):
    if (SuperChType[i]!='0'):
      #      SuperChSeedingLayers[i*2]=4
      #      SuperChSeedingLayers[i*2+1]=2
      SuperChSeedingLayers[i*2]=4
      SuperChSeedingLayers[i*2+1]=2
      break

print(SuperChSeedingLayers)

from Configuration.StandardSequences.Eras import eras

process = cms.Process('RECO',eras.phase2_muon)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Analysis.GEMQC8.GeometryGEMCosmicStand_cff')
process.load('Configuration.StandardSequences.MagneticField_0T_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.RecoSim_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# DEFINITION OF THE SUPERCHAMBERS INSIDE THE STAND
for i in xrange(len(SuperChType)):
  column_row = '_c%d_r%d' % ((i/5)+1, i%5+1)
  if SuperChType[i]=='L' : size = 'L'
  if SuperChType[i]=='S' : size = 'S'
  if SuperChType[i]!='0' :
    geomFile = 'Analysis/GEMQC8/data/gem11'+size+column_row+'.xml'
      print(geomFile)
    if SuperChType[i]!='0' :
      process.XMLIdealGeometryESSource.geomXMLFiles.append(geomFile)
      print('-> Appended')

# Config importation & settings
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.eventsPerJob))
nIdxJob = int(options.idxJob)
strOutput = "out_reco_MC.root" if nIdxJob >= 0 else runConfig.OutputFileName
if nIdxJob < 0: nIdxJob = 0


import os
fpath =  "/eos/cms/store/group/dpg_gem/comm_gem/QC8_Commissioning/run000078/"
# Input source
process.source = cms.Source(
                            "GEMLocalModeDataSource",
                            fileNames = cms.untracked.vstring ([fpath+x for x in os.listdir(fpath) if x.endswith(".dat")]),
                            skipEvents=cms.untracked.uint32(0),
                            fedId = cms.untracked.int32(1472 ),  # which fedID to assign
                            hasFerolHeader = cms.untracked.bool(False),
                            runNumber = cms.untracked.int32(71),
                            )
process.options = cms.untracked.PSet(
                                     SkipEvent = cms.untracked.vstring('ProductNotFound')
                                     )
############## DB file #################
from CondCore.CondDB.CondDB_cfi import *
CondDB.DBParameters.authenticationPath = cms.untracked.string('/afs/cern.ch/cms/DB/conddb')
CondDB.connect = cms.string('sqlite_fip:Analysis/GEMQC8/data/GEMeMap.db')

process.GEMCabling = cms.ESSource("PoolDBESSource",
                                  CondDB,
                                  toGet = cms.VPSet(cms.PSet(
                                                             record = cms.string('GEMeMapRcd'),
                                                             tag = cms.string('GEMeMap_v3')
                                                             )),
                                  )
####################################

process.MessageLogger.cerr.FwkReport.reportEvery = 1000
# validation event filter
process.load('EventFilter.L1TRawToDigi.validationEventFilter_cfi')

process.load('EventFilter.L1TRawToDigi.tmtFilter_cfi')
process.tmtFilter.mpList = cms.untracked.vint32(options.mps)

# Additional output definition
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

# raw to digi
process.load('EventFilter.GEMRawToDigi.muonGEMDigis_cfi')
process.muonGEMDigis.InputLabel = cms.InputTag("source","gemLocalModeDataSource")
process.muonGEMDigis.useDBEMap = True
process.muonGEMDigis.unPackStatusDigis = True

# digi to reco
process.load('RecoLocalMuon.GEMRecHit.gemRecHits_cfi')

process.gemRecHits = cms.EDProducer("GEMRecHitProducer",
                                    recAlgoConfig = cms.PSet(),
                                    recAlgo = cms.string('GEMRecHitStandardAlgo'),
                                    gemDigiLabel = cms.InputTag("muonGEMDigis"),
                                    )

# Reconstruction of muon track
process.load('RecoMuon.TrackingTools.MuonServiceProxy_cff')
process.MuonServiceProxy.ServiceParameters.Propagators.append('StraightLinePropagator')

process.GEMCosmicMuonForQC8 = cms.EDProducer("GEMCosmicMuonForQC8",
                                             process.MuonServiceProxy,
                                             gemRecHitLabel = cms.InputTag("gemRecHits"),
                                             maxClusterSize = cms.double(runConfig.maxClusterSize),
                                             minClusterSize = cms.double(runConfig.minClusterSize),
                                             trackChi2 = cms.double(runConfig.trackChi2),
                                             trackResX = cms.double(runConfig.trackResX),
                                             trackResY = cms.double(runConfig.trackResY),
                                             MulSigmaOnWindow = cms.double(runConfig.MulSigmaOnWindow),
                                             SuperChamberType = cms.vstring(SuperChType),
                                             SuperChamberSeedingLayers = cms.vdouble(SuperChSeedingLayers),
                                             MuonSmootherParameters = cms.PSet(
                                                                               PropagatorAlong = cms.string('SteppingHelixPropagatorAny'),
                                                                               PropagatorOpposite = cms.string('SteppingHelixPropagatorAny'),
                                                                               RescalingFactor = cms.double(5.0)
                                                                               ),
                                             )
process.GEMCosmicMuonForQC8.ServiceParameters.GEMLayers = cms.untracked.bool(True)
process.GEMCosmicMuonForQC8.ServiceParameters.CSCLayers = cms.untracked.bool(False)
process.GEMCosmicMuonForQC8.ServiceParameters.RPCLayers = cms.bool(False)

fScale = 1.0

# Validation
process.gemcrValidation = cms.EDProducer('gemcrValidation',
                                         process.MuonServiceProxy,
                                         verboseSimHit = cms.untracked.int32(1),
                                         simInputLabel = cms.InputTag('g4SimHits',"MuonGEMHits"),
                                         genVtx = cms.InputTag("generator","unsmeared", "RECO"),
                                         recHitsInputLabel = cms.InputTag('gemRecHits'),
                                         tracksInputLabel = cms.InputTag('GEMCosmicMuonForQC8','','RECO'),
                                         seedInputLabel = cms.InputTag('GEMCosmicMuonForQC8','','RECO'),
                                         trajInputLabel = cms.InputTag('GEMCosmicMuonForQC8','','RECO'),
                                         chNoInputLabel = cms.InputTag('GEMCosmicMuonForQC8','','RECO'),
                                         seedTypeInputLabel = cms.InputTag('GEMCosmicMuonForQC8','','RECO'),
                                         genParticleLabel = cms.InputTag('genParticles','','RECO'),
                                         gemDigiLabel = cms.InputTag("muonGEMDigis","","RECO"),
                                         nBinGlobalZR = cms.untracked.vdouble(200,200,200,150,180,250),
                                         RangeGlobalZR = cms.untracked.vdouble(564,572,786,794,786,802,110,260,170,350,100,350),
                                         maxClusterSize = cms.double(runConfig.maxClusterSize),
                                         minClusterSize = cms.double(runConfig.minClusterSize),
                                         maxResidual = cms.double(runConfig.maxResidual),
                                         isMC = cms.bool(False),
                                         SuperChamberType = cms.vstring(SuperChType),
                                         SuperChamberSeedingLayers = cms.vdouble(SuperChSeedingLayers),
                                         MuonSmootherParameters = cms.PSet(
                                                                           PropagatorAlong = cms.string('SteppingHelixPropagatorAny'),
                                                                           PropagatorOpposite = cms.string('SteppingHelixPropagatorAny'),
                                                                           RescalingFactor = cms.double(5.0)
                                                                           )
                                         )

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string('temp_'+strOutput)
                                   )

# Path and EndPath definitions
process.rawTOhits_step = cms.Path(process.muonGEMDigis+process.gemRecHits)
process.reconstruction_step = cms.Path(process.GEMCosmicMuonForQC8)
process.validation_step = cms.Path(process.gemcrValidation)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.rawTOhits_step,
                                process.reconstruction_step,
                                process.validation_step,
                                process.endjob_step
                                )

# enable validation event filtering
process.rawTOhits_step.remove(process.validationEventFilter)
process.rawTOhits_step.remove(process.tmtFilter)
