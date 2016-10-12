#
# (c) 2015-2016 NYU WIRELESS
#

import config

import os, random, string, time, subprocess
from sqlalchemy import create_engine, MetaData, Column, Table
from sqlalchemy import Integer, String
from sqlalchemy.orm import sessionmaker


# Translation/parsing tools
noise=string.whitespace+string.punctuation.replace("-","")
fixer=string.maketrans(noise," "*len(noise))
fixer=string.maketrans("a","a")

def resetSQLMode():
  pengine   = create_engine("mysql://portia:nyuwireless@localhost/arcis",
                       echo=False)
  pmetadata = MetaData(bind = pengine)
  pSession  = sessionmaker(bind = pengine)
  psession  = pSession()
  pconn     = pengine.connect() 
  resetstr  = "SET GLOBAL sql_mode=(SELECT REPLACE(REPLACE(@@sql_mode,"
  resetstr += "'ONLY_FULL_GROUP_BY',''),'STRICT_TRANS_TABLES',''));"
  q = pconn.execute(resetstr)
  q.close()
  pconn.close()

def formSQL(post):

  # Make a copy of the relevant POST entries
  form = {}
  for k in post.keys():
    if post[k].strip() == "": continue
    if k == "sessionID": continue
    if k == "campaign": continue
    form[k] = post[k]

  parameters = []
  strparameters = []
  attributes = []
  repeats = {} 

  # Pre-process for "BETWEEN" clauses
  for k in form.keys():
    if(k[:-1] in attributes):
      repeats[k[:-1]] = []
    else:
      attributes.append(k[:-1])

  # Actually parse the form
  for k in form.keys():
    if(k[:-1] in repeats):
      try:
        repeats[k[:-1]].append(int(form[k]))
      except: pass
      continue
    if k[-1]=="1":
      parameters.append("(attribute='"+k[:-1]+"' AND value >='"+form[k]+"')")
    elif k[-1]=="2":
      if ("(attribute='"+k[:-1]+"' AND value >='"+form[k].value+"')") in parameters:
        parameters.remove("(attribute='"+k[:-1]+"' AND value >='"+form[k]+"')")
        parameters.append("(attribute='"+k[:-1]+"' AND value ='"+form[k]+"')")
      else:
        parameters.append("(attribute='"+k[:-1]+"' AND value <='"+form[k]+"')")
    else:
      strparameters.append("(attribute='"+k+"' AND value ='"+form[k]+"')")

  # Add in repeated values
  for k in repeats.keys():
    sta =  "(attribute='" + k + "' AND (value BETWEEN "
    if len(repeats[k]) < 1: continue
    sta += str(min(repeats[k])) + " AND " + str(max(repeats[k])) + "))"
    parameters.append(sta)

  return parameters, strparameters, len(set(attributes))


# Takes attributes and formats them into meaningful HTML
def getQueryOptions( strAttributes, numAttributes, conn, strDB, numDB, post ):
  queryOptionsString = ""

  # If we have no valid attributes, inform the user
  if len(strAttributes)+len(numAttributes) == 0:
    queryOptionsString  = "<br><br><br>\n<h1>The query parameters you specified "
    queryOptionsString += "yield an empty dataset.</h1>\n<h2>Please 'Clear Query'"
    queryOptionsString += " above or click the back button on your browser.</h2>\n"
    return queryOptionsString  
    
  # Otherwise: process string attributes first ...
  for i in reversed(sorted(strAttributes)):
    if "date" in i: continue
    if "notes" in i: continue
    if i.lower() == "raw pdp filename": continue
    if i.lower() == "filename": continue

    uniques = sorted([ str(x).strip("(),''").rstrip("L") for x in \
      conn.execute("SELECT DISTINCT value FROM " + strDB + " WHERE attribute='" + i + "';") ])

    queryOptionsString += """<div class="queryOption">\n  <span class="queryTitle">"""
    if i=="tx id": queryOptionsString += "TX ID"
    elif i=="rx id": queryOptionsString += "RX ID"
    elif i=="environment": queryOptionsString += "Environment"
    else: queryOptionsString += i.title()
    queryOptionsString += "</span>"

    if len(uniques) > 1:
      queryOptionsString += "<br><br><br><br>\n  <select name='" + i.translate(fixer) + """' >\n    <option value=""></option>\n"""
      for u in uniques:
        if u == "_x001_": continue   # Future-proof
        if i.translate(fixer) in post.keys():
          if post[i.translate(fixer)] == u:
            queryOptionString += "    <option value='" + u.upper() + "' selected>" + u + "</option>\n"
        queryOptionsString += "    <option value='" + u.upper()+"'>" + u.upper() + "</option>\n"
      queryOptionsString += "  </select><br><br>\n"
    else:
      queryOptionsString += "<br><br><br><h3>" + uniques[0][0:20].upper() 
      if len(uniques[0]) > 20: queryOptionsString += " ..."
      queryOptionsString += "</h3>\n"
      if i.translate(fixer) in post.keys():
        queryOptionsString += "<input type=hidden name='" + i.translate(fixer) + "' value='" + post[i.translate(fixer)] + "'>"
    queryOptionsString += "</div>\n"

  # ... then the numerical attributes.
  for i in reversed(sorted(numAttributes)):
    mini, maxi = "", ""
    preset = False
    if i.translate(fixer) + "1" in post.keys():
      mini = post[i.translate(fixer) + "1"]
      preset = True
    if i.translate(fixer) + "2" in post.keys():
      maxi = post[i.translate(fixer) + "2"]
      preset = True

    queryOptionsString += """<div class="queryOption">\n"""

    if False: 
      pass
    else:
      queryOptionsString += """  <span class="queryTitle">""" + i.title() + "</span>\n"

    # Change SQL SELECT statement to one query SELECT min(value), max(value)
    min_val = str(conn.execute("SELECT min(value) FROM " + numDB + " WHERE attribute='" + i + "'"";").fetchone()).strip("(),").rstrip("L")
    max_val = str(conn.execute("SELECT max(value) FROM " + numDB + " WHERE attribute='" + i + "'"";").fetchone()).strip("(),").rstrip("L")
    if min_val == max_val:
      if i == 'carrier frequency': 
        queryOptionsString += "<br><br><br><h3>28.0</h3>"
      else:
        queryOptionsString += "<br><br><br><h3>"
        queryOptionsString += "%.1f" % float(min_val)
        queryOptionsString += "</h3>"
      if mini: queryOptionsString += "<input type=hidden name='" + i.translate(fixer) + "1' value=" + mini + ">"
      if maxi: queryOptionsString += "<input type=hidden name='" + i.translate(fixer) + "2' value=" + maxi + ">"
    else:
      queryOptionsString += "<h4>Min: <textarea id='" + i + """1' onChange="protect('""" + i
      queryOptionsString += """1')" rows=1 cols=12 name='""" + i.translate(fixer) + "1' placeholder="
      queryOptionsString += "%.1f" % float(min_val)
      queryOptionsString += ">" + mini + "</textarea></h4>"
      queryOptionsString += "<h4>Max: <textarea id='" + i + """2' onChange="protect('""" + i
      queryOptionsString += """2')" rows=1 cols=12 name='""" + i.translate(fixer) + "2' placeholder="
      queryOptionsString += "%.1f" % float(max_val)
      queryOptionsString += ">" + maxi + "</textarea></h4>"

    queryOptionsString += "</div>\n"


  # Return the fully formatted string
  return queryOptionsString


# Takes a list of files and formats them to proper HTML
def getFileList(fileList):
  fileListString = ""
  for fname in fileList:
    fileListString += """<span class="listItem" onClick="switchCanvas('"""
    fileListString += fname[:-17] + """');">"""
    fileListString += fname[:-17].replace("_"," ") + "</span><br>\n"
  return fileListString

# Returns html-formatted response for a query to sql database given by 
# key-values in post along with campaign string
def queryDatabase(post, campaigns):

  QUERY_OPTIONS = ""
  IMG_FILENAMES = "" 
  NAVBAR        = ""
  STATBAR       = ""

  postKeys = post.keys()

  # Set up database-specific names
  WNUM = "WIRELESS_num"
  WSTR = "WIRELESS_string"
  CAMPAIGN = campaigns[0]
  if "campaign" in postKeys:
    CAMPAIGN = post["campaign"]
  if "GHz" not in CAMPAIGN:
    pass
  WNUM = WNUM + "_" + CAMPAIGN
  WSTR = WSTR + "_" + CAMPAIGN

  nextCampaign = campaigns[0]
  if CAMPAIGN in campaigns:
    nextIndex = campaigns.index(CAMPAIGN) + 1
    if nextIndex >= len(campaigns): nextIndex = 0
    nextCampaign = campaigns[nextIndex]

  # Open connection with mysql
  engine = create_engine("mysql://portia:nyuwireless@localhost/arcis", echo=False)
  metadata = MetaData(bind = engine)
  Session = sessionmaker(bind = engine)
  session = Session()
  conn = engine.connect()

  # Some query-specific information
  sessionID = ""
  currentNumDB = ""
  currentStrDB = ""
  count = 0
  if len(postKeys) < 2:
    # If this is a vanilla request
    sessionID = "s" + str(time.time()).replace(".","")+str(random.randint(0,100))
    currentNumDB = "" + WNUM + ""
    currentStrDB = "" + WSTR + ""
    countquery = conn.execute("SELECT count( DISTINCT file ) FROM " + WNUM + "")
    count = str(countquery.fetchone()).strip("'L(),")
    countquery.close()
  else:
    # Otherwise, attempt to recover information about the session
    sessionID = str(post["sessionID"])    
    currentNumDB=sessionID+"_SurvivingNum"
    currentStrDB=sessionID+"_SurvivingString"
    conn = engine.connect()
    
    # Try to clean up first
    try: conn.execute("DROP TABLE " + sessionID + "_survived")
    except: pass

    # Set up / recover query tables
    masterTable = Table(sessionID+"_master", metadata,
          Column('id', Integer, primary_key=True),
          Column('file', String(250))
          )
    survived = Table(sessionID+"_survived", metadata,
          Column('id', Integer, primary_key=True),
          Column('file', String(250)),
          Column('cid', Integer)
          )
    survivingNum = Table(currentNumDB, metadata,
          Column('id', Integer, primary_key=True),
          Column('file', String(250)),
          Column('attribute', String(250)),
          Column('value', Integer),
          )
    survivingStr = Table(currentStrDB, metadata,
          Column('id', Integer, primary_key=True),
          Column('file', String(250)),
          Column('attribute', String(250)),
          Column('value', String(100)),
          )   
    metadata.create_all(engine)

    # Parse the post data
    numparameters, strparameters, numAttributes = formSQL(post)
    parameters = numparameters + strparameters
    SQLbase = "INSERT INTO " + sessionID + "_master(file) " 
    SQLstr = ""
    SQLnum = ""

    if len(strparameters) > 0:
      SQLstr="SELECT file FROM " + WSTR + " WHERE " + " OR ".join(strparameters)
    if len(numparameters) > 0:
      SQLnum="SELECT file FROM " + WNUM + " WHERE "  + " OR ".join(numparameters)

    # There are two optimizations that we can do here:
    # (1) Keep track of the current session - subset of the number and string tables -
    # And associate those tables with the constraints you already have. For every
    # "Possible Values" hit, update a table, don't rebuild it. 
    # (2) If there is only n+1 constraints in relation to the previous query, use
    # a simple SELECT to fill the surviving data table
    # For now all queries are taken from the original tables.
    # Note: Original tables are not indexed as there is no particular benefit 
    # from indexing at the moment. (Not enough distinct values in any string column) 
    if SQLstr: 
      insertStr = conn.execute(SQLbase+SQLstr)
      insertStr.close()
    if SQLnum: 
      insertNum = conn.execute(SQLbase+SQLnum)
      insertNum.close()
    cidMake = conn.execute("INSERT INTO "+sessionID+"_survived(id,file,cid) SELECT id, file," \
      + " count(id) as cid from " + sessionID + "_master GROUP BY file HAVING cid=" + str(numAttributes))
    cidMake.close()
    indexMake = conn.execute("CREATE INDEX fileidindex ON "+sessionID+"_survived(file)")
    indexMake.close()
    # ????
    intMake = conn.execute("INSERT INTO " + currentNumDB + "(id,file,attribute,value) SELECT " \
      + WNUM + ".id, " + WNUM + ".file, " + WNUM + ".attribute, " + WNUM + ".value FROM " + WNUM \
      + ", " + sessionID + "_survived WHERE " + WNUM + ".file = " + sessionID + "_survived.file")
    intMake.close()
    strMake=conn.execute("INSERT INTO " + currentStrDB + "(id,file,attribute,value) SELECT " + WSTR \
      + ".id, " + WSTR + ".file, " + WSTR + ".attribute, " + WSTR + ".value FROM " + WSTR + ",  " \
      + sessionID + "_survived WHERE " + WSTR + ".file = " + sessionID + "_survived.file")
    strMake.close()
    countquery = conn.execute("SELECT count( DISTINCT file ) FROM "+sessionID+"_survived")
    count = str(countquery.fetchone()).strip("'L(),")
    countquery.close()

  # Get statistics about the "full" dataset we're querying against  
  totalnumquery = conn.execute("SELECT COUNT(DISTINCT file) from " + WSTR + "")
  totalNumber = str(totalnumquery.fetchone()).strip("'L(),")

  # Populate a list of all valid files
  listOfValidFiles = []
  if int(count) == int(totalNumber):
    listOfValidFiles = [ x[0] for x in conn.execute("SELECT DISTINCT file FROM " + WSTR + "").fetchall() ]
  else:
    listOfValidFiles = [ x[0] for x in conn.execute("SELECT DISTINCT file FROM " + sessionID + "_survived").fetchall() ]
  listOfValidFiles.sort()

  # Sort the valid file list into a meaningful format for HTML list
  IMG_FILENAMES = getFileList( listOfValidFiles )

  # Get attributes from query table
  numAttributes = [ str(x).strip(string.punctuation) for x in conn.execute("SELECT DISTINCT attribute FROM " + currentNumDB) ]
  strAttributes = [ str(x).strip(string.punctuation) for x in conn.execute("SELECT DISTINCT attribute FROM " + currentStrDB) ]

  # Read the returns from the query and reformat them into "HTML meaningful"
  QUERY_OPTIONS = getQueryOptions( strAttributes, numAttributes, conn, currentStrDB, currentNumDB, post )

  # Implement clean-up
  if currentNumDB != ""+WNUM+"":
    tables2Drop = [sessionID+"_master"]
    if currentNumDB != "" + WNUM + "": tables2Drop.append(currentNumDB)
    if currentNumDB != "" + WSTR + "": tables2Drop.append(currentStrDB)
    dropper=conn.execute("DROP TABLE "+" , ".join(tables2Drop))
    dropper.close()

  # Set up the navbar buttons
  NAVBAR += """<input id="frequency" type=reset value='Cycle Campaign (""" 
  NAVBAR += CAMPAIGN.replace('_',' ') + """)'"""
  NAVBAR += """ onClick=ReDirect("query?campaign=""" + nextCampaign + """")>"""
  NAVBAR += """<input id= "queryButton" type=submit value='Download Queried Files ("""
  NAVBAR += str(len(listOfValidFiles)) + "/" + str(totalNumber) + """)' onClick=Direct("dl")>"""
  NAVBAR += """<input id="poss" type=submit value='Filter' onClick=Direct("query?campaign="""
  NAVBAR += CAMPAIGN + """")>"""
  NAVBAR += """<input type=reset value='Clear Query' onClick=ReDirect("query?campaign="""
  NAVBAR += CAMPAIGN + """")>"""
  NAVBAR += """<input type=hidden name=sessionID value=""" + sessionID + ">"
  NAVBAR += """<input type=hidden name=campaign value=""" + CAMPAIGN + """>"""

  # Set up canvas string
  CANV = """  canvas.src="dynamic_img?c=""" + CAMPAIGN + """&i="+str;"""

  # Set up statbar string
  percentage = 100.0 * float("{0:.3f}".format(1.0 * len(listOfValidFiles) / int(totalNumber)))
  STATBAR = """svg.append("rect")"""
  STATBAR += """   .attr("x",0)"""
  STATBAR += """   .attr("y",1)"""
  STATBAR += """   .attr("width",'""" + str(percentage) + """%')"""
  STATBAR += """   .attr("height",48)"""
  STATBAR += """   .attr("fill","#e46a50");"""
  STATBAR += """svg.append("text")"""
  STATBAR += """   .text('""" + str(percentage) + """% of full database')"""

  return [QUERY_OPTIONS, IMG_FILENAMES, NAVBAR, CANV, STATBAR]

def dl(post):

  # Get dev/null
  devnull = open(os.devnull)

  MSG = ""
  FILES = ""

  # String config
  sessionID = post['sessionID']
  ZIPPER_FOLDER = config.FILES_DIR + "/"
  USER_FOLDER = config.FILES_DIR + "/"
  Q1  = "SELECT DISTINCT file FROM " + post['sessionID'] + "_survived"
  Q2  = "SELECT DISTINCT WIRELESS_string_" + post['campaign'] + ".file, "
  Q2 += "WIRELESS_string_" + post['campaign'] + ".file2 from WIRELESS_string_" 
  Q2 += post['campaign'] + ", " + post['sessionID'] + "_survived where WIRELESS_string_" 
  Q2 += post['campaign'] + ".file = " + post['sessionID'] + "_survived.file;"

  print(Q2)

  # Get information from SQL database
  engine = create_engine("mysql://portia:nyuwireless@localhost/arcis",
                       echo=False)
  metadata = MetaData(bind = engine)
  Session = sessionmaker(bind = engine)
  session = Session()
  conn = engine.connect() 

  try:
    query = conn.execute(Q2)
  except:
    Q2  = "SELECT DISTINCT file,file2 FROM WIRELESS_string_" + post['campaign'] + ";"
    query = conn.execute(Q2)
  
  qlist = [ [x[0],x[1]] for x in query.fetchall() ]

  # Collect the files, zip them, and clean up
  try:
    os.mkdir(ZIPPER_FOLDER + post['sessionID'])
  except OSError: pass
  for x,y in qlist:
    subprocess.call([ "cp",config.DATA_ROOT + "/" + post['campaign'] + \
                      "/ProcessedDB/" + str(x),
                      ZIPPER_FOLDER + sessionID + "/" + str(x) ])
  wdir = os.getcwd()
  os.chdir(ZIPPER_FOLDER+sessionID + "/..")
  subprocess.call(["zip","-r",sessionID+".zip",sessionID], 
                    stdout=devnull, stderr=devnull)
  os.chdir(wdir)
  subprocess.call(["rm","-rf",ZIPPER_FOLDER+sessionID])

  # Get -h size
  fSize = os.path.getsize(USER_FOLDER+"/"+sessionID+".zip")
  if (fSize > 1024**3):
    fileSize = str(int(fSize/1024/1024/1024)+1) + "GB"
  elif (fSize > 1024**2):
    fileSize = str(int(fSize/1024/1024)+1) + "MB"
  else:
    fileSize = str(int(fSize/1024)+1) + "KB"

  # More string formatting
  MSG  = "A new zip folder has been created at<br><tt>" + USER_FOLDER + \
          "/"+sessionID+".zip</tt><br>containing the queried files."
  MSG += " The filesize is " + fileSize + "."
  MSG = MSG.replace("//","/")

  # Write file information
  FILES  = "<p>The following files (" + str(len(qlist)) + ") are contained:</p>\n"
  FILES += "<pre>\n<div class=\"tube\"><div class=\"tube\">\n"
  for y,x in qlist:
    xp = x.strip().lower()
    if xp == "na": 
      FILES += str(y) + "\n"
    else:
      FILES += str(xp) + "\n"
  FILES += "</div></div>"

  return MSG, FILES


