#! /usr/bin/env python
import ROOT
import sys
import os
from DataFormats.FWLite import Events, Handle
from array import array
import math

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='data1.root',help="File to be analyzed.")
    parser.add_argument("-n","--nEvents",default=0,type=int,help="Number of events to process.")
    parser.add_argument("-m","--maxPrint",default=10,type=int,help="Maximum number of events to print.")
    return parser.parse_args()


def printEvent(muons, vertices) :
    print("Muons\n #   Q      pt     eta     phi  iVtx")
    for i in range(len(muons)) :
        vtxList = ''
        for j in range(len(muons[i].vtxIndx())) :
            vtxList += " {0:2d}".format(muons[i].vtxIndx()[j])

        print("{0:2d}{1:5.1f}{2:8.2f}{3:8.2f}{4:8.2f}{5:s}".format(
            i,muons[i].charge(),muons[i].pt(),muons[i].eta(),muons[i].phi(),vtxList))

    print("Vertices\n #    x       y       z   ")
    for i in range(len(vertices)) :
        print("{0:2d}{1:8.3f}{2:8.3f}{3:8.3f}".format(i,vertices[i].x(),vertices[i].y(),vertices[i].z()))

    return

# begin execution here 

args = getArgs()
nPrint = args.maxPrint 

# Events takes either
# - single file name
# - list of file names
# - VarParsing options
events = Events (args.inFileName) 

# create handle outside of loop
handleMu  = Handle ("std::vector<ScoutingMuon>")
labelMu = ("hltScoutingMuonPackerCalo")
handleTrg = Handle ("edm::TriggerResults")
labelTrg = ("TriggerResults")
handleVtxDisp = Handle ("std::vector<ScoutingVertex>")
labelVtxDisp = ("hltScoutingMuonPackerCalo","displacedVtx")

ROOT.gROOT.SetBatch()        
ROOT.gROOT.SetStyle('Plain') 

hM_mumuOS = ROOT.TH1F ("mumuOS", "mumuOS", 100, 0., 100)
hM_mumuSS = ROOT.TH1F ("mumuSS", "mumuSS", 100, 0., 1.)
hM_munum = ROOT.TH1F ("munum", "munum", 20, 0., 20.)

# double_mu_counts = 0

# loop over events
print("Entering event loop") 
for kl, event in enumerate(events) :
    if kl % 1000 == 0 : print("Reading event {0:d}".format(kl)) 
    aux = event.eventAuxiliary()

    event.getByLabel (labelMu, handleMu)  
    muons = handleMu.product()

    event.getByLabel (labelVtxDisp, handleVtxDisp)  
    vertices = handleVtxDisp.product()

    numMuons = len (muons)

    hM_munum.Fill(numMuons+0.1)

    if numMuons < 2: continue#4: continue

    muon1 = ROOT.TLorentzVector ()
    muon2 = ROOT.TLorentzVector ()
    #muon3 = ROOT.TLorentzVector ()
    #muon4 = ROOT.TLorentzVector ()

    muon1.SetPtEtaPhiM(muons[0].pt(), muons[0].eta(), muons[0].phi(), 0.10566)
    muon2.SetPtEtaPhiM(muons[1].pt(), muons[1].eta(), muons[1].phi(), 0.10566)
    #muon3.SetPtEtaPhiM(muons[2].pt(), muons[2].eta(), muons[2].phi(), 0.10566)
    #muon4.SetPtEtaPhiM(muons[3].pt(), muons[3].eta(), muons[3].phi(), 0.10566)

    invMass = (muon1+muon2).M()#+muon3+muon4).M()

    #if (invMass <= 0.212) :
     #   printEvent()

    #if (muons[0].charge()*muons[1].charge()*muons[2].charge()*muons[3].charge()) > 0 and int(muons[0].charge()+muons[1].charge()+muons[2].charge()+muons[3].charge())==0:
    if (muons[0].charge()*muons[1].charge()<0):
        hM_mumuOS.Fill(invMass)
        #print("\n\nM_mumu={0:.5f}".format(invMass))
        #printEvent(muons, vertices)
    else :
        hM_mumuSS.Fill(invMass)

    #if (nPrint > 0 and len(vertices) > 1) or numMuons > 3: 
    #    nPrint -= 1
    #    print("\n\nM_mumu={0:.5f}".format(invMass))
    #    printEvent(muons,vertices)
        
    if args.nEvents > 0 and kl > args.nEvents : break

i = 0
while os.path.exists("hist%s.root" % i):
    i += 1

outputFile=ROOT.TFile("hist%s.root"%i,"recreate")


hM_mumuOS.Write()
hM_mumuSS.Write()
hM_munum.Write()
outputFile.Write()
outputFile.Close()

# print("Double Mu Counts: " + str(double_mu_counts))
