# Written by Patrick Jenkins on 8/7/2009 for the people's mbta.
#
# A hack to get the bus times. Reads in 'bus_routes.txt' and looks up each
# bus schedule and places it into a dictionary.
import HTMLParser
import pickle
import simplejson
import sys
import urllib

from xml.marshal.generic import Marshaller

class MyHTMLParser(HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.in_timetable = False
    self.in_timetable_row = False
    self.in_timetable_cell = False
    self.in_timetable_label_cell = False
    self.found_timetable_labels = False
    self.current_cell_value = ""
    self.labels = []
    self.all_runs = []
    self.current_run = []

  def handle_starttag(self, tag, attrs):
    if ("div" == tag and 
        0 != len(attrs) and 
        "timetable" == attrs[0][1]):
      self.in_timetable = True
      #print "In timetable"
    elif ("tr" == tag and 
          self.in_timetable):
      self.current_run = []
      self.in_timetable_row = True
      #print "entering timetable row";
    elif ("td" == tag and 
          self.in_timetable and
          self.in_timetable_row):
      self.in_timetable_cell = True
      self.current_cell_value = ""
      #print "In timetable cell"
    elif ("th" == tag and 
          self.in_timetable and
          self.in_timetable_row):
      self.in_timetable_label_cell = True
      self.current_cell_value = ""
      #print "In timetable label cell"

  def handle_endtag(self, tag):
    if ("tr" == tag and 
        self.in_timetable and
        self.in_timetable_row):
      #print "Leaving timetable row"
      if (not self.found_timetable_labels):
        self.found_timetable_labels = True
      else: 
        self.all_runs.append(self.current_run)
      #print "We now have found "+str(len(self.all_runs))+" runs with "+str(len(self.current_run))+" stops\n";
      self.in_timetable_row = False
    elif ("td" == tag and
          self.in_timetable and
          self.in_timetable_row and
          self.in_timetable_cell):
      self.in_timetable_cell = False
      self.current_run.append(self.current_cell_value)
      #print "Leaving timetable cell"
    elif ("th" == tag and
          self.in_timetable and
          self.in_timetable_row and
          self.in_timetable_label_cell):
      self.in_timetable_label_cell = False
      self.labels.append(self.current_cell_value)
      #print "Leaving timetable label cell"
    elif ("div" == tag and
          self.in_timetable):
      self.in_timetable = False

  def handle_data(self, data):
    if (self.in_timetable and
        self.in_timetable_row and
        (self.in_timetable_label_cell or self.in_timetable_cell)):
      #print "Found cell"
      self.current_cell_value += data

f = open('./bus_routes.txt', 'r')
route_name_list = f.readlines()
f.close()
p = MyHTMLParser()

directions= [("O", "Outbound"), ("I", "Inbound")]
timing = [("W", "Weekday"), ("S", "Saturday"), ("U","Sunday")]

all_routes = dict()
for route_name in route_name_list:
  route_name = route_name.strip()
  sub_routes = dict()
  for direction in directions:
    sub_routes[direction[1]] = dict()
    for time in timing:
      url = "http://www.mbta.com/schedules_and_maps/bus/routes/?route=" + route_name + "&direction=" + direction[0] + "&timing=" + time[0]
      print url
      html = urllib.urlopen(url).read().replace("\r\n", "")
      #try:
      p.feed(html)
      sub_routes[direction[1]][time[1]] = dict()
      sub_routes[direction[1]][time[1]]['stops'] = p.labels
      sub_routes[direction[1]][time[1]]['times'] = p.all_runs
      #except Exception, e:
      #print str(e)
      p.reset()
      p.labels = []
      p.all_runs = []
      p.current_run = []
      p.in_timetable = False
  all_routes[route_name] = sub_routes
  simplejson.dump(all_routes, open('routes.json', 'w'))
  marshal = Marshaller()
  marshal.dump(all_routes, open('routes.xml', 'w'))
