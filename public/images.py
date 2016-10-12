# 
# (c) 2015 NYU WIRELESS
# 

import config

def dynamic_img( post ):

  img = open(config.PUBLIC_DIR + '/no_img.png'.format(),"rb").read() 

  try:
    itype = ""
    campg = ""
    try: itype = post['i']
    except: pass
    try: campg = post['c']
    except: pass
    
    if itype == "map":
      ipath = config.PUBLIC_DIR + "/map" + campg + ".png"
      img = open(ipath.format(),"rb").read()

    else:
      itype = itype.replace('trackavg','track1')
      ipath = config.DATA_ROOT + '/' + campg + "/PngDB/" + itype + ".png"
      img = open(ipath.format(),"rb").read()

  except:
    print("This should not appear in the log: image pass...")

  return img

