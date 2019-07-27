import csv
import os
import sys
import io
import subprocess
import time

if __name__ == '__main__':

    run_number = sys.argv[1]

    # Different paths definition
    srcPath = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0]+'QC8Test/src/'
    pyhtonModulesPath = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0]+'QC8Test/src/Analysis/GEMQC8/python/'
    runPath = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/test/'
    configTablesPath = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/StandConfigurationTables/'
    alignmentTablesPath = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/StandAligmentTables/'
    deadStripsTablesPath = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/DeadStripsTables/'
    hotStripsTablesPath = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/HotStripsTables/'
    resDirPath = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0]

    sys.path.insert(0,pyhtonModulesPath)

    import config_creator
    import geometry_files_creator
    import convertHotDeadStripsTables
    import dbTableToHotDeadStripsTable

    # Generate configuration file
    config_creator.configMaker(run_number)
    time.sleep(1)

    # Generate geometry files
    geometry_files_creator.geomMaker(run_number,"--noAlignment")
    time.sleep(1)

    # Compiling after the generation of the geometry files
    scramCommand = "scram build -j 4"
    scramming = subprocess.Popen(scramCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=srcPath)
    while scramming.poll() is None:
        line = scramming.stdout.readline()
        print(line)
    print scramming.stdout.read()
    scramming.communicate()
    time.sleep(1)

    # Running the CMSSW code
    runCommand = "cmsRun -n 8 runGEMCosmicStand_hot_dead_strips.py"
    running = subprocess.Popen(runCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    while running.poll() is None:
        line = running.stdout.readline()
        print(line)
    print running.stdout.read()
    running.communicate()
    time.sleep(1)

    #  # Creating folder outside the CMMSW release to put the output files and plots
    outDirName = "Results_QC8_hot_dead_strips_run_"+run_number
    #---# Remove old version if want to recreate
    if (os.path.exists(resDirPath+outDirName)):
        rmDirCommand = "rm -rf "+outDirName
        rmDir = subprocess.Popen(rmDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=resDirPath)
        rmDir.communicate()
    #---# Create the new empty folder
    resDirCommand = "mkdir "+outDirName
    resDir = subprocess.Popen(resDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=resDirPath)
    resDir.communicate()
    time.sleep(1)

    # Create folders for ouput plots per chamber
    import configureRun_cfi as runConfig
    SuperChType = runConfig.StandConfiguration
    effoutDir = os.path.abspath("launcher_hot_dead_strips.py").split('QC8Test')[0] + outDirName
    for i in range (0,30):
        if (SuperChType[int(i/2)] != '0'):
            plotsDirCommand = "mkdir outPlots_Chamber_Pos_" + str(i)
            plotsDirChamber = subprocess.Popen(plotsDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=effoutDir)
            plotsDirChamber.communicate()
    time.sleep(1)

    # Selecting the correct output file, changing the name and moving to the output folder
    out_name = 'out_run_'
    for i in range(6-len(run_number)):
        out_name = out_name + '0'
    out_name = out_name + run_number + '.root'

    mvToDirCommand = "mv hot_dead_strips_" + out_name + " " + resDirPath+outDirName + "/hot_dead_strips_" + out_name
    movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    movingToDir.communicate()
    time.sleep(1)

    # Efficiency computation & output
    effCommand = "root -l -q " + runPath + "macro_hot_dead_strips.c(" + run_number + ",\"" + configTablesPath + "\")"
    efficiency = subprocess.Popen(effCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=effoutDir)
    while efficiency.poll() is None:
        line = efficiency.stdout.readline()
        print(line)
    print efficiency.stdout.read()
    efficiency.communicate()
    time.sleep(1)

    # Moving the output of the root analysis to the folder in GEMQC8/data/..
    out_name = 'DeadStrips_run' + run_number + '_ToDB.csv'
    mvToDirCommand = "cp " + effoutDir + "/" + out_name + " " + deadStripsTablesPath + out_name
    movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    movingToDir.communicate()
    time.sleep(1)
    out_name = 'HotStrips_run' + run_number + '_ToDB.csv'
    mvToDirCommand = "cp " + effoutDir + "/" + out_name + " " + hotStripsTablesPath + out_name
    movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    movingToDir.communicate()
    time.sleep(1)

    # Converting tables ToDB-like into FromDB-like
    convertHotDeadStripsTables.convertHotDead(run_number,"hot")
    convertHotDeadStripsTables.convertHotDead(run_number,"dead")

    # Convert FromDB-Like tables into CMSSW-like tables
    dbTableToHotDeadStripsTable.SwMappingHotDeadStrips(run_number,"hot")
    dbTableToHotDeadStripsTable.SwMappingHotDeadStrips(run_number,"dead")
