# (C) 2017 IBM
# Author: Nishanth Antony Satler, Visakan Bapu, Anitt Rajendran, Yuvaraj Subramanian`
#
# Very short sample app used with Db2 Warehouse on Cloud to demonstrate
# how to use a SQL Cloud Database with a web app.

import os
from flask import Flask,redirect,render_template,request
import urllib
import datetime
import json
import ibm_db
import get_sentiment_review

app = Flask(__name__)

#get service information if on IBM Cloud Platform
if 'VCAP_SERVICES' in os.environ:
   appenv = json.loads(os.environ['VCAP_APPLICATION'])
else:
    raise ValueError('Expected cloud environment')


db2cred = {}
db2cred['db'] = 'BLUDB'
db2cred['hostname'] = 'dashdb-entry-yp-dal09-09.services.dal.bluemix.net'
db2cred['port'] = '50000'
db2cred['username'] = 'dash11634'
db2cred['password']='sx_f8IBR8_wU'



# handle database request
def review(name=None):
    # connect to DB2
    db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")
    if db2conn:
        # we have a Db2 connection, query the database
        sql="select * from NLP_YELP_REVIEWS FETCH FIRST 20 ROWS ONLY"
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.
        stmt = ibm_db.prepare(db2conn,sql)
        #ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)

		#Format the Date Object
        for row in rows:
            row['DATE'] = str(row['DATE'])
		
        # close database connection
        ibm_db.close(db2conn)
	if(request.args.get('json')=='true'):
		return json.dumps(rows)
	else:
		return render_template('review.html', ci=rows)

# handle database request
def retBusiness(name=None):
    # connect to DB2
    db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")
    if db2conn:
        sql = "select * from BUSINESS_LDA_SAMPLES"
        if(request.args.get('Cuisine')!= None and request.args.get('Cuisine')!=''):
            sql =sql+ " where \"categories\" like '%"+request.args.get('Cuisine')+"%'"
        if(request.args.get('Location')!= None and request.args.get('Location')!=''):
            sql = sql+ " and \"city\"='"+request.args.get('Location')+"'"
        sql = sql +" order by \"averaged_star_value\" desc FETCH FIRST 20 ROWS ONLY"
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.
        stmt = ibm_db.prepare(db2conn,sql)
        #ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
		
        # close database connection
        ibm_db.close(db2conn)
	return json.dumps(rows)


# main page to dump some environment information
@app.route('/')
def index():
   return render_template('MainChatWindow.html', app=appenv)

# for testing purposes - use name in URI
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/search', methods=['GET'])
def searchroute():
    name = request.args.get('name', '')
    return json.dumps(name)

@app.route('/review', methods=['GET'])
def reviewroute():
	return review(None)

@app.route('/business', methods=['GET'])
def businesses():
	return retBusiness(None)

@app.route('/sentiment', methods=['GET'])
def sentimentvalues():
    review = request.args.get('textReview')
    return json.dumps(get_sentiment_review.get_sentiment_values(review))

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
