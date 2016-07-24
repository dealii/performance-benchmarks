# timo.heister@gmail.com

import os
import sys
import fileinput
import json as js
from dateutil import parser
import datetime

def load_ref():
    ref = {}
    try:
        f = open("ref.db", 'r')
    except IOError:
        return ref

    ref = js.loads(f.read())
    f.close()

    return ref

ref = load_ref()

class DB:
    def __init__(self):
        # entry with sha1 as key
        # entry is dict() with sha1, time, record
        # record is a dict with name->time 
        self.data = dict()
        self.dbname = "render.db"

    def load(self):
        try:
            f = open(self.dbname, 'r')
        except IOError:
            self.save()
            return

        text = f.read()
        f.close()
        self.data = js.loads(text)

    def save(self):
        text = js.dumps(self.data)
        f = open(self.dbname, 'w')
        f.write(text)
        f.close()

    def dump(self):
        print "dumping {0} entries".format(len(self.data))

        for sha in self.data:
            x = self.data[sha]
            print x['sha1'], x['desc'], x['time'], x['record'] 
            #print "{} {} {} {}".format(x['sha1'], 0, x['good'], x['name'])

    def get(self, sha):
        if not sha in self.data:
            self.data[sha]=dict()
            self.data[sha]['sha1']=sha
            self.data[sha]['time']=0
            self.data[sha]['record']=dict()
        
        return self.data[sha]
        
    def render(self):
        timeshatable={}
        series={}

        # sort by time:
        keys = []
        for x in self.data.values():
            try:
                keys.append((x['sha1'], parser.parse(x['time'])))
            except ValueError:
                print "could not parse date for {}".format(x['sha1'])
        
        keys = [ k[0] for k in sorted(keys, key=lambda x: x[1], reverse=True) ]
        
        for sha in keys:
            x = self.data[sha]
            timedate = parser.parse(x['time']).isoformat()
            timeshatable[timedate] = x['desc']
            for name in x['record']:
                seconds = x['record'][name]
                if not name in series:
                    series[name]=[]
                series[name].append( [ timedate, seconds ] )
            
        print """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
        <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <title>deal.II automated benchmarks</title>
                
                
                <!-- 1. Add these JavaScript inclusions in the head of your page -->
                <script type="text/javascript" src="http://code.jquery.com/jquery-1.9.1.min.js"></script>
                <script type="text/javascript" src="http://code.highcharts.com/highcharts.js"></script>
                <script type="text/javascript" src="http://code.highcharts.com/modules/data.js"></script>
                
                
                <!-- 2. Add the JavaScript to initialize the chart on document ready -->
                <script type="text/javascript">
        """
        print "shas={};"
        for time in timeshatable:
            print "shas[Date.parse(\"{}\").toString()]=\"{}\";".format(time, timeshatable[time])

        print "ref={};"
        for s in ref:
            print "ref[\"{}\"]={};".format(s, ref[s])

        print """
                $(document).ready(function() {                      
                            $('#container').highcharts({
                                chart: {
type: 'line',
                marginRight: 250,
                marginBottom: 25,
                zoomType: 'x'
                                },

series: [
"""
        sortedkeys = sorted(series.keys())
        for s in sortedkeys:
            print "{"
            print "name: '{}',".format(s)
            print "data: ["

            sorted_series = sorted(series[s], key=lambda x: parser.parse(x[0]))

            for d in sorted_series:
                ref_value = ref[s] if s in ref else 1.0
                v = d[1]/ref_value*100# - 100
                print "[Date.parse(\"{}\"), {}],".format(d[0], v)
            print "] },"

        print """
],
            title: {
                text: 'regression timings',
                x: -20 //center
            },
                xAxis: {
            type: 'datetime',
            /*dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'*/
            },
            yAxis: {
                title: {
                    text: 'perc'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                shared: false,
                crosshairs: true,
                formatter: function() {
                        return '<b>'+ this.series.name +'</b><br/>'+
                        Math.round(this.y) + '% of ' + ref[this.series.name]
                + ', rev ' + shas[this.x] + ' at ' + Highcharts.dateFormat('%A, %b %e, %Y', this.x);
                }
            },
            plotOptions: {
            line: {
                marker: {
                    enabled: true
                }
            },
                series: {
                    cursor: 'pointer',
                    point: {
                       events: {
                            click: function (e) {
                  alert(shas[this.x]);
                            }
                        }
                    },
                    marker: {
                        lineWidth: 2
                    }
                }
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'top',
                x: -10,
                y: 100,
                borderWidth: 0
            },
                

                            });
//                      });

if (0)                        
             setTimeout(function(){
chart = $('#container').highcharts();
chart.xAxis[0].setExtremes(Date.parse("2015-07-28T13:45:48-05:00"),chart.xAxis[0].getExtremes().dataMax); 
},2000);           
                });

                </script>
                
        </head>
        <body>
<a href="https://www.dealii.org">deal.II</a> performance benchmarks, see 
<a href="https://www.dealii.org/developer/developers/testsuite.html">testsuite documentation</a> for more info.<br>
                <p>Last update: """
        print str(datetime.datetime.now())
        print """</p>

                <div id="container" style="width: 1200px; height: 600px; margin: 0 auto"></div>
                
                                
        </body>
</html>
"""

        

db = DB()
db.load()

whattodo = ""

if len(sys.argv)<2:
    print "usage: record <sha>|render"
else:
    whattodo=sys.argv[1]

if whattodo=="record":
    lines=[l.replace("\n","") for l in sys.stdin]
    sha=lines.pop(0)
    testname=lines.pop(0)
    desc=lines.pop(0)
    time=lines.pop(0)

    obj=db.get(sha)
    obj['desc']=desc
    obj['time']=time
    record=obj['record']
    for line in lines:
        parts = line.split(" ")
        name = parts[1].strip()
        time = parts[2].strip()
        if len(name)>0:
            name = testname+":"+name
            time = float(time)
            if not name in record:
                record[name]=time
            else:
                record[name]=min(time, record[name])

    db.save()
    #print sha, record

if whattodo=="dump":
    db.dump()
if whattodo=="render":
    db.render()




