# Juan Felipe Beltran jfb325@nyu.edu
# Last Updated: March 21, 2013

import os
import sys
import commands
import string	
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String, Float

## Edit things here
DATA_FOLDER = "/../data/73GHz_Indoor_Foliage/ProcessedDB"
REF_FOLDER  = "/../reference"
META_FOLDER = "/../data/73GHz_Indoor_Foliage/MetaDB"
POST_FIX = "_73GHz_Indoor_Foliage"
VERBOSE=True

# Or alternatively, load them from the command line...
if len(sys.argv) > 1:
  DATA_FOLDER = "/../data/" + sys.argv[1] + "/ProcessedDB"
  META_FOLDER = "/../data/" + sys.argv[1] + "/MetaDB"
  POST_FIX    = "_" + sys.argv[1]

### No need to modify anything below here
RUN_DIR = os.getcwd()
DATA_FOLDER = RUN_DIR + DATA_FOLDER
META_FOLDER = RUN_DIR + META_FOLDER
REF_FOLDER  = RUN_DIR + REF_FOLDER
if not os.path.exists("./../reference"): os.makedirs("./../reference")

#Remove whitespace and punctuation from filename string, leave extensions intact.
def cleanString(s):
	junk=string.whitespace+string.punctuation.replace(".","").replace("_","")
	fixer=string.maketrans(junk," "*len(junk))
	return s.translate(fixer).replace(" ","").lower()

engine = create_engine("mysql://portia:nyuwireless@localhost/arcis",
                       echo=True)
 
metadata = MetaData(bind = engine)
 
num_table = Table('WIRELESS_num'+POST_FIX, metadata,
                    Column('id', Integer, primary_key=True),
                    Column('file', String(250)),
		    Column('file2',String(250)),
                    Column('attribute', String(250)),
                    Column('value', Float),   # Integer vs Float
                    )
                    
string_table = Table('WIRELESS_string'+POST_FIX, metadata,
                    Column('id', Integer, primary_key=True),
                    Column('file', String(250)),
                    Column('file2',String(250)),
		    Column('attribute', String(250)),
                    Column('value', String(100)),
                    )         
                    
metadata.create_all(engine)
conn = engine.connect()
                  
#Returns True if number is floatable
def isFloat(num):
	if num.strip() == "":
		return True
	try:
		float(num.strip().split(" ")[0])
		return True
	except (ValueError, TypeError):
		return False

#Takes in logfile text and returns a dictionary {field:value}
def parseLog(path,logfile):
	logfile=logfile.strip().lower().split("\n")
	logfile=[[y.strip() for y in x.split("=")] for x in logfile if "=" in x]
	logfile=filter(None,[x for x in logfile if len(x)==2])
	finallog={}
	for line in logfile:
		name, value = line
		finallog[name]=value
	finallog["filename"]=path
	return finallog
	
#Finds every possible field described in the group of Log Dictionaries, returns list
def getFields(dictGroup):
	parameters=[]
	for i in dictGroup:
		parameters.extend(i.keys())
	parameters=list(set(parameters))
	return parameters

def toNumber(value):
	numbers=value.strip(string.letters+string.whitespace)
	try:
		return str(float(numbers))
	except (TypeError,ValueError):
		return value

#Creates all files required for the website to run
def populateDB():
	#Fetch Log Information
	home=commands.getoutput("pwd")
	os.chdir(DATA_FOLDER)
	logDict={x:open(x).read().strip() for x in commands.getoutput("ls").strip().split("\n")}
	logs=[parseLog(x,logDict[x]) for x in logDict.keys()]
	fields= getFields(logs)
	
	#Delete Past Files
	os.chdir(REF_FOLDER)
	print [commands.getoutput("rm "+x) for x in commands.getoutput("ls").split("\n") if "." in x]
	
	#fields.remove("filename")
	
	types={"Dropdown":[],"Max/Min":[]}
	for i in fields:
		if False not in [isFloat(log[i]) for log in logs if i in log.keys()]:
			types["Max/Min"].append(i)
		else:
			types["Dropdown"].append(i)
	for log in logs:
		try: 
			filename2={x.strip():y.strip() for x,y in [z.split("=") for z in open(META_FOLDER+cleanString(log["raw pdp filename"].replace(".txt","_meta.txt"))).read().strip().split("\n")]}["fn"]
		except:
			filename2="NA"
		for t in types["Max/Min"]:
			if t in log.keys():
				if len(log[t].strip().split(" "))>1:
					unit=" "+log[t].strip().split(" ")[-1]
				else:
					unit=""
				batch= num_table.insert().values(file=log["filename"],file2=filename2 ,attribute=t+unit , value=float(log[t].strip().split(" ")[0]))
				if VERBOSE: print(t+unit+"\t\t"+str(log[t].strip().split(" ")[0])+"\t\t"+str(conn.execute(batch)))	
		for t in types["Dropdown"]:
			if t in log.keys():
				batch= string_table.insert().values(file=log["filename"],file2=filename2, attribute=t, value=str(log[t]))
				if VERBOSE: print(t+"\t\t"+str(log[t])+"\t\t"+str(conn.execute(batch)))
		
	print "ALL DONE"
	print "Max/Mins found: "+str(types["Max/Min"])
	print "Dropdown found: "+str(types["Dropdown"])
	
	conn.execute("CREATE INDEX stringIndex ON WIRELESS_string"+POST_FIX+"(attribute,value,id,file,file2)")
	
	conn.close()
	os.chdir(home)

if __name__ == "__main__":
  populateDB()
  print("\nUpdating campaign file...")
  othercampaigns = [ sys.argv[1].replace('.tar','') ]
  try:
    sys.path.append("./../public")
    import campaigns
    for c in campaigns.CAMPAIGNS: 
      if c not in othercampaigns: 
        othercampaigns.append(c)
  except:
    pass
  try:
    fptr = open('./../public/campaigns.py','w')
    fptr.write("#\n# (c) 2015 NYU WIRELESS\n#\n\nCAMPAIGNS = [\n")
    for c in othercampaigns:
      fptr.write("\"{0:s}\",\n".format(c))
    fptr.write("]\n\n")
    fptr.close()
  except:
    print("\nUnable to write campaign file. Campaign not added!\n")

  print("Done!")


