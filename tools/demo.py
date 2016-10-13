#
#  Generates a "demo_package.tar" file which contains
#  everything necessary to take propdb out for a test
#  drive!
#
# /Package
# /Package/MetaDB
# /Package/PngDB
# /Package/ProcessedDB
# /Package/RawDB
#

import os
import random
import numpy as np
from subprocess import call
import matplotlib.pyplot as plt

def writeProcessed(rootdir,info):
  f = open(rootdir + "/ProcessedDB/" + info["name"]+"_processedlog.txt","w")
  f.write("TX ID=" + info["txid"] + "\n")
  f.write("RX ID=" + info["rxid"] + "\n")
  f.write("Measurement Number=" + info["meas"] + "\n")
  f.write("Track Number=" + info["track"] + "\n")
  f.write("Step=" + info["step"] + "\n")
  f.write("Rotation Number=" + info["rot"] + "\n")
  f.write("TX Height=" + info["txheight"] + "\n")
  f.write("RX Height=" + info["rxheight"] + "\n")
  f.write(info["block1"])
  f.write("RX Antenna Polarization=" + info["rxpol"] + "\n")
  f.write("Environment=" + info["env"] + "\n")
  f.write("TR Separation=" + info["trsep"] + "\n")
  f.write("AOD Azimuth=90\nAOD Elevation=10\nAOA Azimuth=")
  f.write(info["aoaazi"] + "\nAOA Elevation=-10\n")
  f.write("Pr=" + info["power"] + "\n")
  f.write("Total PL" + info["pathloss"] + "\n")
  f.write(info["block2"])
  f.write("Number of Multipath Components=" + info["multipath"] + "\n")
  f.write(info["block3"])
  f.write(info["block4"])
  f.write("Raw PDP Filename=" + info["rawfname"] + "\n\n")
  f.close()

def writePng(rootdir,info,t,pdp):
  fig = plt.figure()
  plt.plot(t,pdp)
  plt.title("TX Location: " + info["txid"] + ", RX Location: " + info["rxid"])
  plt.xlabel("Excess Delay (ns)")
  plt.ylabel("Received Power (dBm/ns)")
  plt.savefig(rootdir + "/PngDB/" + info["name"] + ".png")
  plt.close(fig)

def writeMeta(rootdir,info):
  f = open(rootdir+"/MetaDB/"+info["rawfname"].replace(".txt","")+"_meta.txt","w")
  f.write("fn=" + info["name"] + "\n\n")
  f.close()


if __name__ == "__main__":

  ## Set up environment
  rootdir = "./temp/Package/"
  if not os.path.exists(rootdir): os.makedirs(rootdir)
  else: print("temp/Package directory exists. Exiting."); exit(1)
  os.makedirs(rootdir+"MetaDB")
  os.makedirs(rootdir+"PngDB")
  os.makedirs(rootdir+"ProcessedDB")
  os.makedirs(rootdir+"RawDB")

  for TX in ["MTC 1", "COL 2", "KAU 3"]:
    print("Creating PDPs for TX " + TX)
    for RX in ["1","2","3","4"]:
      TRSEP = random.random() * 100 + 10
      for MEAS in range(1,4):
        for TRACK in range(1,2):
          for STEP in range(1,2):
            for ROT in range(12):
              info = {}
              info["txid"] = TX
              info["rxid"] = RX
              info["meas"] = str(MEAS)
              info["track"] = str(TRACK)
              info["step"] = str(STEP)
              info["rot"] = str(ROT)
              info["txheight"] = "2.5"
              info["rxheight"] = "1.5"
              info["block1"] = "Carrier Frequency=7.35E+10\nTX Antenna Gain=20\n"
              info["block1"] += "TX Antenna Azimuth HPBW=15\nTX Antenna Elevation HPBW=15\n"
              info["block1"] += "TX Antenna Polarization=V\nRX Antenna Gain=20\n"
              info["block1"] += "RX Antenna Azimuth HPBW=15\nRX Antenna Elevation HPBW=15\n"
              if MEAS==1: info["rxpol"] = "V"
              else: info["rxpol"] = "H"
              if MEAS<3: info["env"] = "LOS"
              else: info["env"] = "NLOS"
              info["trsep"] = str(TRSEP)
              info["aoaazi"] = str(ROT*30)
              info["power"] = str(-1.0 * random.random()*80 - 20)
              info["pathloss"] = str(random.random()*50+50)
              info["block2"] = "PL w.r.t. Free Space Reference Distance=24.4179\n"
              info["block2"] += "Free Space Calibration Distance=4\nPLE w.r.t. 1m "
              info["block2"] += "Free Space Reference Distance=2.7203\nTX Power=-7.9\n"
              info["block2"] += "TX PN Chip Rate=400000000\nNoise Threshold before "
              info["block2"] += "Processing Gain=-90.1849\n"
              n_mpath = random.randint(2,10)
              maxtime = random.random()*100+20
              maxpower = random.random()*40+20
              t = np.arange(0,maxtime,0.1)
              pdp = np.zeros(len(t)) - 80 + random.random()*10
              pdp += maxpower * np.exp(-pow((t-2.5),2.0)/4.0)
              for i in range(n_mpath-1):
                t0 = random.random()*100+10
                path = maxpower / 4.0 * (random.random()*2+1) * np.exp(-pow((t-t0),2.0)/4.0)
                path *= np.exp(- t / maxtime)
                pdp += path
              info["multipath"] = str(n_mpath) + "\nMultipath Time Resolution=2.5"
              info["block3"] = "RMS Delay Spread=" + str(random.random()*10+2.0) + "\n"
              info["block3"] += "Maximum Peak Delay=" + "3.125" + "\n"
              info["block3"] += "Maximum Excess Delay 10 dB Down from Max Peak=17.5625" + "\n"
              info["block3"] += "Maximum Excess Delay 20 dB Down from Max Peak=18.625" + "\n"
              info["block4"] = "Measurement Date=09.10.11\nCalibration Folder Number=1\nSweep Type=RXSweep\n"
              info["rawfname"] = "IQsquared_" + TX + "_" + RX + "_" + str(MEAS) + str(STEP) + "_" + str(ROT)
              info["rawfname"] += str(info["aoaazi"]) + str(random.randint(0,100)) + "_1.txt"
              info["rawfname"] = info["rawfname"].replace(" ","")
              info["name"] = info["txid"] + "_" + info["rxid"] + "_meas" + info["meas"]
              info["name"] += "_rot" + info["rot"] + "_rx_az_" + info["aoaazi"] + "_tx_az_90_pdp"

              writeProcessed(rootdir,info)
              writePng(rootdir,info,t,pdp)
              writeMeta(rootdir,info)

  ## Archive everything & clean environment
  oldpath = os.getcwd()
  os.chdir("temp")
  call(["tar", "-cvf", "demo_package.tar", "Package/"])
  call(["mv", "demo_package.tar", ".."])
  call(["rm", "-rf", "Package"])
  os.chdir(oldpath)
