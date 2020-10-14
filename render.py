# timo.heister@gmail.com

import os
import sys
import fileinput
import json as js
from dateutil import parser
import datetime

# offline rendering:
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import base64
import numpy as np

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
        print("dumping {0} entries".format(len(self.data)))

        for sha in self.data:
            x = self.data[sha]
            print(x['sha1'], x['desc'], x['time'], x['record'])
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
                print("could not parse date for {}".format(x['sha1']))
        
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
            
        print("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
        <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <title>deal.II automated benchmarks</title>

<style>
.mytable, .mytable td, .mytable th {
  border: 1px solid black;
  border-collapse: collapse;
  font-family:"Lucida Console", Monaco, monospace;
}
.mytable td + td {text-align:right; }
</style>
                <!-- 1. Add these JavaScript inclusions in the head of your page -->
                <script type="text/javascript" src="http://code.jquery.com/jquery-1.9.1.min.js"></script>
                <script type="text/javascript" src="http://code.highcharts.com/highcharts.js"></script>
                <script type="text/javascript" src="http://code.highcharts.com/modules/data.js"></script>
                
                
                <!-- 2. Add the JavaScript to initialize the chart on document ready -->
                <script type="text/javascript">
        """)
        print("shas={};")
        for time in timeshatable:
            print("shas[Date.parse(\"{}\").toString()]=\"{}\";".format(time, timeshatable[time]))

        print("ref={};")
        for s in ref:
            print("ref[\"{}\"]={};".format(s, ref[s]))

        print("""
                $(document).ready(function() {                      
                            $('#container').highcharts({
                                chart: {
type: 'line',
                marginRight: 250,
                marginBottom: 25,
                zoomType: 'xy'
                                },

series: [
""")
        sortedkeys = sorted(series.keys())
        for s in sortedkeys:
            print("{")
            print("name: '{}',".format(s))
            print("data: [")

            sorted_series = sorted(series[s], key=lambda x: parser.parse(x[0]))

            for d in sorted_series:
                ref_value = ref[s] if s in ref else 1.0
                v = d[1]/ref_value*100# - 100
                v = d[1]
                print("[Date.parse(\"{}\"), {}],".format(d[0], v))
            print("] },")

        print("""
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
                        Math.round(this.y/100.0*ref[this.series.name]*1000.0)/1000.0 + ', ' + 
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
                <p>Last update: """)
        print(str(datetime.datetime.now()))
        print("</p>")


        # overview table
        cols=5
        revs=[]
        for i in range(0,cols):
            revs.append(keys[i])
        revs.append("e42ced414f930a6708997032ee0e2b19e668cba2") # 9.2
        revs.append("777cf92a41deba5c03ec8b561e7fb76d8c5f7249") # 9.1.1
        revs = revs[::-1]
        
        print("""<table class=mytable>
        <tr>
        <th></th>""")
        for sha in revs:
            x = self.data[sha]
            print("<th><a href='https://github.com/dealii/dealii/commit/{}'>{}</a></th>".format(x['desc'], x['desc']))
        print("</tr>")

        for key in sortedkeys:
            print("<tr>")
            print("<td>{}</td>".format(key))
            for sha in revs:
                x = self.data[sha]
                value = "?" if not key in x['record'] else x['record'][key]
                print("<td>{:.3f}</td>".format(value))
            print("</tr>")
        
        print("</table>")

        # array of shas and descriptions sorted by time:
        sha_arr = keys[::-1]
        descriptions_arr = [self.data[sha]['desc'] for sha in sha_arr]
        sha_to_index = {}
        for idx in range(len(sha_arr)):
            sha_to_index[sha_arr[idx]]=idx
        
        # map name -> np values
        series_y = {}
        for idx in range(len(sha_arr)):
            sha = sha_arr[idx]
            x = self.data[sha]
            for name in x['record']:
                if not name in series_y:
                    series_y[name]=len(sha_arr)*[np.nan]
                seconds = x['record'][name]
                series_y[name][idx] = seconds

        # plots
        print("<br><br>")
        
        #data_uri = base64.b64encode(open('test.png', 'rb').read()).decode('utf-8')
        #img_tag = '<img src="data:image/png;base64,{0}">'.format(data_uri)
        #print(img_tag)


        lastprog = sortedkeys[0].split(":")[0]
        xx = np.arange(len(sha_arr))

        def finish_plot(title):
            plt.title(lastprog)
            plt.xticks(xx, descriptions_arr, rotation='vertical', fontsize=7)
            plt.savefig("cache.png")
            plt.cla()
            data_uri = base64.b64encode(open('cache.png', 'rb').read()).decode('utf-8')
            img_tag = '<br><img src="data:image/png;base64,{0}"/><br>'.format(data_uri)
            print(img_tag)
        
        for s in sortedkeys:
            name = s
            prog = s.split(":")[0]
            if prog!=lastprog:
                finish_plot(lastprog)
                 
            lastprog=prog
            
            #print("name: '{}',".format(s))
            plt.plot(xx, series_y[s],'*-',label=s)
            

        finish_plot(lastprog)

        # all data:
        
        
        # dynamic plot:
        print("<br><br>")
        print("""<div id="container" style="width: 1200px; height: 600px; margin: 0 auto"></div>""")
        
        print("</body></html>")

db = DB()
db.load()

whattodo = ""

if len(sys.argv)<2:
    print("usage:")
    print("  record <sha>")
    print("  render")
    print("  dump")
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
    print("recorded", sha)

if whattodo=="dump":
    db.dump()
if whattodo=="render":
    db.render()




