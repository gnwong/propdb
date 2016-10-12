#
# Performs the following steps:
# 

from subprocess import call

# Check if pip installed
ret = call(["which","pip"])
if ret != 0:
  print("pip not found. Please run the following")
  print("from the command line (with sudo privileges):\n")
  print(" sudo apt-get install python-pip python-dev build-essential")
  print(" sudo -H pip install --upgrade pip")
  print(" sudo -H pip install --upgrade virtualenv")
  exit(-1)

# Check if mysql is installed
ret = call(["which","mysql"])
if ret != 0:
  print("mysqldb not found. Please run the following")
  print("from the command line (with sudo privileges):\n")
  print(" sudo apt-get install python-dev libmysqlclient-dev ")
  print(" sudo -H pip install MYSQL-python")
  print(" sudo apt-get install mysql-server")
  exit(-1)

# Verify necessary libraries are installed
dep_web = True
dep_sql = True
dep_xlr = True
print("\nChecking for dependencies...")
try:
  from sqlalchemy import create_engine
  print("... sqlalchemy installed!")
  dep_sql = False
except:
  dep_sql = True
try:
  import web
  print("... web.py installed!")
  dep_web = False
except:
  dep_web = True
try:
  import xlrd
  print("... xlrd installed!")
except:
  dep_xlr = False
if (dep_sql or dep_web or dep_xlr):
  print("Required library not found. Please run the following")
  print("from the command line (with sudo privileges):\n")
  istring = " sudo -H pip install"
  if dep_sql: istring += " sqlalchemy"
  if dep_web: istring += " web.py"
  if dep_xlr: istring += " xlrd"
  print(istring)
  print("\nAfter installing the above, please re-run this script.\n\n")
  exit(-1)

import os, sys
from getpass import getpass
from sqlalchemy import create_engine

reset = False
if "-reset" in sys.argv:  reset = True

# Set up mysql
print("\nEnter root password FOR MYSQL below or leave blank if not set.")
mysql_password = getpass("password: ")
engine = create_engine("mysql://root:{0:s}@localhost".format(mysql_password),echo=False)
mysql_success = False
try:
  conn = engine.connect()
  mysql_success = True
  conn.close()
except:
  mysql_success = False
if not mysql_success:
  print("\nUnable to connect to mysql database.\n> Is it running?\n> Was the password correct?")
  exit(1)

conn = engine.connect() # Connect to database

if reset:
  try: conn.execute("DROP DATABASE arcis;")
  except: pass
  try: conn.execute("DROP USER 'portia'@'localhost';")
  except: pass
  print("\nReset sql database.\n\n")
  exit(0)

# Create database arcis
print("\nAttempting to create new database 'arcis' now!")
try:
  conn.execute("CREATE DATABASE arcis;")
except Exception,e:
  if str(e).find("database exists") != -1:
    print("It seems database 'arcis' already exists. Continuing...")
  else:
    print("Error creating database 'arcis'. Quitting...")
    exit(2)

# Create user portia
print("\nNow creating user 'portia'")
try:
  conn.execute("CREATE USER 'portia'@'localhost' IDENTIFIED BY 'nyuwireless';")  
  # grant super to the user "portia"
  conn.execute("GRANT SUPER ON *.* TO 'portia'@'localhost' IDENTIFIED BY 'nyuwireless';")
  mysql_success = "y"
except Exception,e:
  print("Unable to create user. Perhaps 'portia' already exists?")
  print("Continuing will grant user permissions on database.")
  # grant super to the user "portia"
  conn.execute("GRANT SUPER ON *.* TO 'portia'@'localhost' IDENTIFIED BY 'nyuwireless';")
  mysql_success = raw_input("Continue (y/n): ")
if mysql_success.lower().strip().find("y") == -1:
  print("\nAborting!")
  exit(3)

# Grant permissions
print("\nUpdating permissions...")
try:
  conn.execute("GRANT ALL PRIVILEGES ON arcis.* TO 'portia'@'localhost';")
except Exception,e:
  print("Fatal error granting privileges, aborting!")
  exit(4)

# Update config.py
print("\nWriting system config file...")
try:
  cwd = os.getcwd()[:-5]
  fptr = open('../public/config.py','w')
  fptr.write("#\n# (c) 2015 NYU WIRELESS\n#\n\nimport web\n\nweb.config.debug = False\n\n")
  fptr.write( "PUBLIC_DIR = \"{0:s}public\"\nDATA_ROOT  = \"{0:s}data\"\n".format(cwd,cwd) )
  fptr.write( "FILES_DIR  = \"{0:s}files\"\n\n".format(cwd) )
  fptr.close()
except:
  print("\nUnable to write config file. Aborting!")

# Update campaigns.py
print("\nSetting up clean campaign file...")
othercampaigns = []
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
  print("\nUnable to write campaign file. Aborting!")
  exit(5)

print("\nSuccessfully set up database system!\n\n")

