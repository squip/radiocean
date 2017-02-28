
from flask import render_template, request,  flash, redirect
from app import app
import pickle
import pandas as pd
import pymongo
from pymongo import MongoClient
from .forms import SearchForm
from flask import g
from .forms import LoginForm
from pprint import pprint
from flask import jsonify


# c = pymongo.mongo_client.MongoClient(host='162.243.83.70', port=27017)
# conn = pymongo.Connection()
# db = conn.live_transcription
conn = pymongo.Connection(host='162.243.83.70', port=27017)
db = conn.radioscribe
db.transcribed_segments


@app.before_request
def before_request():
    g.form = SearchForm()

@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    return render_template('header.html')

# @app.route('/index', methods=['GET'])
# def index():
  
#     user = {'nickname': 'SQUIP'}  # fake user

#     query = g.form.search.data
#     return render_template('index.html',
#                           form=g.form,
#                           query=query)



@app.route('/searchy', methods=['GET'])
def searchy():
    # query = g.form.search.data
    return render_template('searchy.html')

@app.route('/header', methods=['GET'])
def header():
    # query = g.form.search.data
    return render_template('header.html')



@app.route('/search', methods=['GET', 'POST'])
def search():
    query = g.form.search.data
    print query


    topics = ['traffic','weather','politics','sports','finance']
    if query in topics:
        text_results = db.command('text', 'transcribed_segments', search=query, limit=10)
	# text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
        # pprint(text_results)
        ids = [res['obj']['id_segment'] for res in text_results['results']]
        # ids = [res['obj']['text'] for res in text_results['results']]        
    else:
        ids = [6,4,5,2,1,4,6]
    return render_template('search_results.html', 
                           results=ids,
                           )


@app.route('/ajax', methods = ['POST'])
def ajax_request():
    query = request.form['username']
    query_orig = query.lower()
    query = query_orig.split()
    query = [str(q) for q in query]
    pprint(query)
    stations = ['kcbs','wbbm','wcbs']
    cities = {'kcbs':'san francisco', 'wbbm':'chicago', 'wcbs':'new york'}
    topics = ['traffic','weather','politics','sports','finance']

    if query[0] in stations:
        if len(query) > 1:
            if query[1] in topics:
                text_results = db.transcribed_segments.find({"label":query[1], "station":query[0]}).limit(10)
		# text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
                pprint(text_results)
                matching_segments = []
                for res in text_results:
                    res['_id'] = str(res['_id'])
                    matching_segments.append(res)
            else:
                query_str = ' '.join(query[1:])
                text_results = db.command('text', 'transcribed_segments', search=query_str, filter={'station':query[0]}, limit=10)
                # text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
		pprint(text_results)
                matching_segments = []
                for res in text_results['results']:
                    res['obj']['_id'] = str(res['obj']['_id'])
                    # res['obj']['file'] = str(res['obj']['_id']
                    matching_segments.append(res['obj'])

        else:
            pprint(query)
            text_results = db.transcribed_segments.find({"station":query[0]}).limit(10)
            # text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
	    pprint(text_results)
            matching_segments = []
            for res in text_results:
                res['_id'] = str(res['_id'])
                matching_segments.append(res)


    elif query[0] in topics:
        if len(query) > 1:
            query_str = ' '.join(query[1:])
            text_results = db.command('text', 'transcribed_segments', search=query_str, filter={'label':query[0]}, limit=10)
            # text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
	    pprint(text_results)
            matching_segments = []
            for res in text_results['results']:
                res['obj']['_id'] = str(res['obj']['_id'])
                matching_segments.append(res['obj'])

        else:
            text_results = db.transcribed_segments.find({"label":query[0]}).limit(10)
            # text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
	    pprint(text_results)
            matching_segments = []
            for res in text_results:
                res['_id'] = str(res['_id'])
                matching_segments.append(res)

    elif [city for city in cities.itervalues() if query_orig.find(city) > -1]:
        station_city = [(station, city) for (station, city) in cities.iteritems() if query_orig.find(city) > -1]
        pprint(station_city[0])
        station = station_city[0][0]
        pprint(station)
        city = station_city[0][1]
        pprint(city)
        city_str_index = query_orig.find(city) + len(city)
        query_str_minus_city = query_orig.replace(city, '')
        query = query_str_minus_city.strip()

        if len(query) > 1:
            if query_orig in [topic for topic in topics if query_orig.find(topic) > -1]:
                label = [topic for topic in topics if query_orig.find(topic) > -1]
                pprint(label)
                text_results = db.transcribed_segments.find({"label":label, "station":station}).limit(10)
                # text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
		pprint(text_results)
                matching_segments = []
                for res in text_results:
                    res['_id'] = str(res['_id'])
                    matching_segments.append(res)
            else:
                text_results = db.command('text', 'transcribed_segments', search=query, filter={'station':station}, limit=10)
                # text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
		pprint(text_results)
                matching_segments = []
                for res in text_results['results']:
                    res['obj']['_id'] = str(res['obj']['_id'])
                    matching_segments.append(res['obj'])

        else:
            text_results = db.transcribed_segments.find({"station":station}).limit(10)
            # text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
	    pprint(text_results)
            matching_segments = []
            for res in text_results:
                res['_id'] = str(res['_id'])
                matching_segments.append(res)


        # else:
        #     if query[0] in topics:
        #         text_results = db.transcribed_segments.find({"label":query[0]}).limit(10)
        #         pprint(text_results)
        #         matching_segments = []
        #         for res in text_results:
        #             # res = str(res)
        #             matching_segments.append(res)

        #     else:
        #         query_str = str(query[0])
        #         text_results = db.command('text', 'transcribed_segments', search=query_str, filter={'station':query[0]}, limit=10)
        #         pprint(text_results)
        #         matching_segments = []
        #         for res in text_results['results']:
        #             res['obj']['_id'] = str(res['obj']['_id'])
        #             matching_segments.append(res)

    # if query[0] in topics:
    #     text_results = db.command('text', 'transcribed_segments', search=query[0], limit=10)
    #     pprint(text_results)
    #     matching_segments = []
    #     for res in text_results['results']:
    #         res['obj']['_id'] = str(res['obj']['_id'])
    #         matching_segments.append(res)


    # else:
    #     matching_segments = [6,4,5,2,1,4,6]
    # pprint(matching_segments)
    # return jsonify(matches=matching_segments)

    else:
        text_results = db.command('text', 'transcribed_segments', search=query_orig, limit=10)
        # text_results = text_results.sort([('id_segment',pymongo.DESCENDING)])
	pprint(text_results)
        matching_segments = []
        for res in text_results['results']:
            res['obj']['_id'] = str(res['obj']['_id'])
            matching_segments.append(res['obj'])
    return jsonify(matches=matching_segments)
