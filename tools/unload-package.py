
import os
from subprocess import call
import sys


pckg_fname = ""
if len(sys.argv) < 2:
	pckg_fname = raw_input("Name of package: ")
else:
	pckg_fname = sys.argv[1]

if not os.path.exists("./../data"): os.makedirs("./../data")
van_list = os.listdir("./")
call(["tar", "-xvf", "./../" + pckg_fname])
up_list = os.listdir("./")
for nme in up_list:
	if nme not in van_list:
		call(["mv", nme, "./../data/" + pckg_fname.replace(".tar","")])

print("\n\nDone.\n\nGoodbye!")
