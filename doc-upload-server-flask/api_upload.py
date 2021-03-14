from flask import Flask,render_template,url_for,request
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

import pandas as pd 
import numpy as np
import pickle

import os
import sys
import requests
import time
import logging

logging.getLogger().setLevel(logging.INFO)

from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

import pymongo
import json
import getopt, pprint

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['.zip','pdf','png', 'jpg', 'jpeg','PNG'])

@app.route('/')
def index():
    return render_template('index_new.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    request_id = request.form['request_id']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    PATH_TO_TEST_IMAGES_DIR = app.config['UPLOAD_FOLDER']
    TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR,filename.format(i)) for i in range(1, 2) ]

    image_path = TEST_IMAGE_PATHS[0]
    filepath = image_path

    # upload to DB here --- 
    # return template saying the doc has been uploaded
    # check this for uploading -- https://stackoverflow.com/questions/58165966/store-a-pdf-file-in-my-mongodb-database-with-pymongo-error
    # # myclient = pymongo.MongoClient('mongodb://192.168.1.104:27017/')
    # myclient = pymongo.MongoClient('mongodb://2.tcp.ngrok.io:14374/')
    # db = myclient['EMP-DB']
    # col = db["Request_DB"]

    # request_data = col.find({'_id':request_id})[0]
    # myquery = { "_id": request_id }
    # newvalues = { "$set": { "reference_doc":doc_upload} }
    # col.update_one(myquery, newvalues)

    return render_template('complete.html', titles = ['Reimbursement Documents'])        

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=2000, debug=True)
