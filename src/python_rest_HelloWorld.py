
# Python Sample Application: Connection to Informix using REST


# Topics
# 1 Inserts
# 1.1 Insert a single document into a collection
# 1.2 Insert multiple documents into a collection
# 2 Queries
# 2.1 Find one document in a collection that matches a query condition  
# 2.2 Find documents in a collection that match a query condition
# 2.3 Find all documents in a collection
# 3 Update documents in a collection
# 4 Delete documents in a collection
# 5 Get a listing of collections
# 6 Drop a collection

import json
import logging
import os
import requests
from flask import Flask, render_template

app = Flask(__name__)

# To run locally, set URL. The url should include the database name.
# Otherwise, url and database information will be parsed from the Bluemix VCAP_SERVICES.
URL = ""
COLLECTION_NAME = "pythonREST"
USE_SSL = False     # Set to True to use SSL url from VCAP_SERVICES
SERVICE_NAME = os.getenv('SERVICE_NAME', 'timeseriesdatabase')
port = int(os.getenv('VCAP_APP_PORT', 8080))

def getDatabaseUrl():
    """
    Get database url
    
    :returns: (url)
    """
    
    # Use defaults
    if URL :
        return URL
    
    # Parse database info from VCAP_SERVICES
    if (os.getenv('VCAP_SERVICES') is None):
        raise Exception("VCAP_SERVICES not set in the environment")
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    try:
        tsdb = vcap_services[SERVICE_NAME][0]
        credentials = tsdb['credentials']
        if USE_SSL:
            url = credentials['rest_url_ssl']
        else:
            url = credentials['rest_url']
        return url
    except KeyError as e:
        logging.error(e)
        raise Exception("Error parsing VCAP_SERVICES. Key " + str(e) + " not found.")

         
def printError(output, message, reply):
    output.append("Error: " + message)
    output.append("status code: " + str(reply.status_code))
    output.append("content: " + str(reply.content))
    
def doEverything():
    # Get database connectivity information
    url = getDatabaseUrl()

    output = []
    output.append("# 1 Inserts")
    output.append( "# 1.1 Insert a single document to a collection")
    data = json.dumps({'name': 'test1', 'value': 1})
    reply = requests.post(url + "/" + COLLECTION_NAME, data)
    # Note: the cookie holds our session id. In order to reuse the same listener session 
    # on subsequent REST requests, we must set this cookie as part of subsequent requests. 
    cookies = reply.cookies  
    if reply.status_code == 200:
        doc = reply.json()
        output.append("inserted " + str(doc.get('n')) + " documents")
    else:
        printError(output, "Unable to insert document", reply)
    
    output.append("# 1.2 Insert multiple documents to a collection")
    data = json.dumps([{'name': 'test1', 'value': 1}, {'name': 'test2', 'value': 2}, {'name': 'test3', 'value': 3} ] )
    reply = requests.post(url + "/" + COLLECTION_NAME, data, cookies=cookies)
    if reply.status_code == 202:
        doc = reply.json()
        output.append("inserted " + str(doc.get('n')) + " documents")
    else:
        printError(output, "Unable to insert multiple documents", reply)
    
    output.append("# 2 Queries")
    output.append("# 2.1 Find a document in a collection that matches a query condition")
    query = json.dumps({'name':'test1'})
    reply = requests.get(url + "/" + COLLECTION_NAME + "?query=" + query, cookies=cookies)
    if reply.status_code == 200:
        doc = reply.json()
        output.append("query result: " + str(doc[0]))
    else:
        printError(output, "Unable to query documents in collection", reply)
          
    output.append("# 2.2 Find all documents in a collection that match a query condition")
    query = json.dumps({'name':'test1'})
    reply = requests.get(url + "/" + COLLECTION_NAME + "?query=" + query, cookies=cookies)
    if reply.status_code == 200:
        doc = reply.json()
        output.append("query result: " + str(doc))
    else:
        printError(output, "Unable to query documents in collection", reply)
                             
#     output.append("# 2.3 Find all documents in a collection")
    reply = requests.get(url+ "/" + COLLECTION_NAME, cookies=cookies)
    if reply.status_code == 200:
        doc = reply.json()
        output.append("query result: " + str(doc))
    else:
        printError(output, "Unable to query documents in collection", reply)
                             
    output.append("# 3 Update documents in a collection")
    query = json.dumps({'name': 'test3'})
    data = json.dumps({'$set' : {'value' : 9} })
    reply = requests.put(url + "/" + COLLECTION_NAME + "?query=" + query, data, cookies=cookies)
    if reply.status_code == 200:
        doc = reply.json()
        output.append("updated " + str(doc.get('n')) + " documents")
    else:
        printError(output, "Unable to update documents in collection", reply)
                             
    output.append("# 4 Delete documents in a collection")
    query = json.dumps({'name': 'test2'})
    reply = requests.delete(url + "/" + COLLECTION_NAME + "?query=" + query, cookies=cookies)
    if reply.status_code == 200:
        doc = reply.json()
        output.append("deleted " + str(doc.get('n')) + " documents")
    else:
        printError(output, "Unable to delete documents in collection", reply)
                             
    output.append("# 5 Get a listing of collections")
    reply = requests.get(url, cookies=cookies)
    if reply.status_code == 200:
        doc = reply.json()
        dbList = ""
        for db in doc:
            dbList += "\'" + db + "\' "
        output.append("Collections: " + str(dbList))
    else:
        printError(output, "Unable to retrieve collection listing", reply)
          
    output.append("# 6 Drop a collection")
    reply = requests.delete(url + "/" + COLLECTION_NAME, cookies=cookies)
    if reply.status_code == 200:
        doc = reply.json()
        output.append("delete collection result: " + str(doc))
    else:
        printError(output, "Unable to drop collection", reply)
    
    return output

@app.route("/")
def displayPage():
    return render_template('index.html')

@app.route("/databasetest")
def runSample():
    output = []
    try:
        output = doEverything()
    except Exception as e:
        logging.exception(e) 
        output.append("EXCEPTION (see log for details): " + str(e))
    return render_template('tests.html', output=output)
 
if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port=port)
