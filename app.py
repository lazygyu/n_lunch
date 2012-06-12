# -*- coding: utf-8 -*-
import pymongo
import random
import json
import toolbox
import urllib
from xml.dom import minidom
from pymongo import Connection
from bson import json_util
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug.contrib.fixers import ProxyFix
# configuration
MAP_APIKEY = 'd19ca444058e82fed60dc1dc2cef323909e45578'
LOCAL_APIKEY = '97b834e4a44793d02a9a4363d0e420fa17b85f0c'
NAVER_APIKEY = 'bedb6502ebaec4a31f6531963162d08a'
SECRET_KEY = 'whereweeatlunch' 
DEBUG = True
LANG = "utf-8"
PREFIX = "/lunch"
app = Flask(__name__)
app.config.from_object(__name__)

def dbCon():
    return Connection('localhost', 27017)

@app.route('/')
def indexPage():
    if request.headers['user-agent'].lower().find("mobile") > -1:
        return redirect(url_for('mobilePage'))
    return redirect(url_for('mainPage'))

@app.route('/m')
def mobilePage():
    return render_template('mobile/main.html', config=app.config)

@app.route('/lunch')
def mainPage():
    conn = dbCon()
    db = conn.lunch
    collection = db.restaurants
    cnt = collection.count()
    return render_template('mainpage.html', config=app.config, rcount=cnt)

@app.route('/about')
def about():
    return render_template('about.html', config=app.config)

@app.route('/recommand')
def recommand():
    conn = dbCon()
    db = conn.lunch
    collection = db.restaurants
    cnt = collection.count()
    if cnt == 0:
        return "no data"
    idx = random.randint(1, cnt)
    result = collection.find().limit(-1).skip(idx-1).next()
    return json.dumps(result, default=json_util.default)

@app.route('/localsearch', methods=['get','post'])
def localsearch():
    param = urllib.urlencode({'key':app.config['NAVER_APIKEY'], 'target':'local', 'query':request.form['key'].encode('utf-8')})
    sock = toolbox.openAnything('http://openapi.naver.com/search?' + param)
    xmldoc = minidom.parse(sock)
    sock.close()
    nodes = xmldoc.getElementsByTagName('item')
    res = []
    dg = ""
    for item in nodes:
        tmp = item.childNodes
        #res.append(tmp.length)
        n_title = tmp[0].firstChild.nodeValue
        n_desc = tmp[2].firstChild.nodeValue if tmp[2].hasChildNodes()==True else ""
        n_tel = tmp[3].hasChildNodes() and tmp[3].firstChild.nodeValue or ""
        n_addr = tmp[4].hasChildNodes() and tmp[4].firstChild.nodeValue or ""
        n_x = tmp[5].firstChild.nodeValue
        n_y = tmp[6].firstChild.nodeValue
        res.append({'title':n_title, 'desc':n_desc, 'tel':n_tel, 'addr':n_addr, 'x':n_x, 'y':n_y})
    xmldoc.unlink()
    return json.dumps(res)
    
@app.route('/add', methods=['get','post'])
def addForm():
    if request.method == 'GET':
        return render_template('addform.html', config=app.config)
    else:
        restaurant = {}
        restaurant['title'] = request.form['title'].encode('utf-8')
        restaurant['addr'] = request.form['addr'].encode('utf-8')
        restaurant['tel'] = request.form['tel'].encode('utf-8')
        restaurant['desc'] = request.form['desc'].encode('utf-8')
        if request.form.has_key('price_min'):
            restaurant['price_min'] = request.form['price_min'].encode('utf-8')
        if request.form.has_key('price_max'):
            restaurant['price_max'] = request.form['price_max'].encode('utf-8')
        if request.form.has_key('roadview'):
            restaurant['viewpoint'] = request.form['viewpoint']
            restaurant['panoId'] = request.form['panoId']
        restaurant['pos'] = {'lat':request.form['lat'], 'lng':request.form['lng']}
        conn = dbCon()
        db = conn.lunch
        collection = db.restaurants
        collection.save(restaurant);
        flash(u'추가되었습니다!')
        return redirect(url_for('mainPage'))
    

app.wsgi_app = ProxyFix(app.wsgi_app)


def start_server():
	app.run(host='0.0.0.0')
	pass

if __name__ == '__main__':	
	start_server()
