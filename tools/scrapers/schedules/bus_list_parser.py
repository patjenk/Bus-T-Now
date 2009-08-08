# Written by Patrick Jenkins on 8/7/2009 for the people's mbta. 
#
# A complete hack to get a list of the bus route names. To use, go to 
# http://www.mbta.com/ and select "Bus" under "Schedules and Interactive Maps."
# Use firebug to copy the html for the select box that is displayed. Place that
# HTML into "bus_routes.html" and then run this script.
import HTMLParser

class MyHTMLParser (HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self) 
    self.in_option_tag=False

  def handle_starttag(self, tag, attrs):
    if ("option" == tag):
      self.in_option_tag=True

  def handle_endtag(self, tag):
    if ("option" == tag):
      self.in_option_tag=False

  def handle_data(self, tag):
    if self.in_option_tag:
      route_messy = tag.split('-')[0]
      print route_messy
      self.in_option_tag=False

f = open('./bus_routes.html', 'r')
html = "\n".join(f.readlines())
f.close()
p = MyHTMLParser()
#try:
p.feed(html)
#except:
#  print "done"
