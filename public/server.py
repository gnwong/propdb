#
# (c) 2016 NYU WIRELESS
#
# 
# Recall: 
#   To tunnel, use
#     ssh -L port1:localhost:port2 user@host
#   where
#     port1  is the local port
#     port2  is the remote port.
#

import web
import images
import config
import campaigns
import sql_interface

# Regex for allowed pages
urls = (
  '/', 'index',
  '/query', 'query',
  '/dl', 'dl',
  '/dynamic_img', 'img'
)

# Set up html templates
render = web.template.render('templates/')

# Class definitions
class index:
  def GET(self):
    raise web.seeother('/query')

class query:
  def GET(self):
    if len(campaigns.CAMPAIGNS)==0: return render.empty()
    [a,b,c,d,e] = sql_interface.queryDatabase( web.input(), campaigns.CAMPAIGNS )
    return render.query(a,b,c,d,e)

  def POST(self):
    if len(campaigns.CAMPAIGNS)==0: return render.empty()
    [a,b,c,d,e] = sql_interface.queryDatabase( web.input(), campaigns.CAMPAIGNS )
    return render.query(a,b,c,d,e)

class dl:
  def GET(self):
    try:
      [a,b] = sql_interface.dl( web.input() )
      return render.dl(a,b)
    except:
      return render.empty()
  def POST(self):
    try:
      [a,b] = sql_interface.dl( web.input() )
      return render.dl(a,b)
    except:
      return render.empty()

class img:
  def GET(self):
    web.header("Content-Type", "image/png")
    return images.dynamic_img( web.input() )
  def POST(self):
    web.header("Content-Type", "image/png")
    return images.dynamic_img( web.input() )

# Start up the server
if __name__ == "__main__":
  sql_interface.resetSQLMode()
  app = web.application(urls, globals())
  app.run()
