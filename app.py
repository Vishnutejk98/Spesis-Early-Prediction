#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template,redirect, url_for, request
import pickle


# In[2]:


app = Flask(__name__,template_folder='templates')
model = pickle.load(open('model.pkl', 'rb'))
flag = False

# Route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if(request.form['username'] == "admin" and request.form['password'] == "admin@123"):
            return redirect(url_for('adminworld'))
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            global flag
            flag  = True
            print(flag)
            return redirect(url_for('reg'))
    return render_template('login.html', error=error)

global username,age,mainsyptoms,address
username = ""
age = ""
mainsyptoms = ""
address = ""
import csv

@app.route('/reg')
def reg():
    global flag
    if flag == True:
        return render_template('registerpaitent.html')
    else:
         return redirect(url_for('login'))


@app.route('/admin')
def adminworld():
    return render_template('admin.html')

@app.route('/register',methods=['POST','GET'])
def register():
    global username,age,mainsyptoms,address
    username = request.values.get("name")
    age = request.values.get("age")
    address = request.values.get("address")
    mainsyptoms = request.values.get("mainsymptoms")
    return redirect(url_for('home'))

@app.route('/home')
def home():
    global flag
    if flag == True:
        return render_template('select.html')
    else:
         return redirect(url_for('login'))
        
@app.route('/deepanalysis')
def deepanalysis():
    global flag
    if flag == True:
        return render_template('index.html')
    else:
         return redirect(url_for('login'))

@app.route('/smartanalysis')
def smartanalysis():
    global flag
    if flag == True:
        return render_template('optimal.html')
    else:
         return redirect(url_for('login'))


@app.route('/logout')
def logout():
    global flag
    flag = False
    return redirect(url_for('login'))


@app.route('/predict',methods=['POST','GET'])
def predict():
    global flag
    if(flag == False):
          return redirect(url_for('login'))
    features = [x for x in request.form.values()]
    final_features = [np.array(features)]
    print(final_features)
    column_names=['HR','O2Sat','Temp','SBP','MAP','DBP','Resp','EtCO2','BaseExcess','HCO3','FiO2','pH','PaCO2','SaO2','AST','BUN','Alkalinephos',
                  'Calcium','Chloride','Creatinine','Bilirubin_direct','Glucose','Lactate','Magnesium','Phosphate','Potassium','Bilirubin_total','TroponinI','Hct','Hgb','PTT','WBC','Fibrinogen','Platelets','Age','Gender','Unit1','Unit2','HospAdmTime','ICULOS']
    final_features=pd.DataFrame(final_features,columns=column_names)
    prediction= model.predict(final_features)
    #print(prediction[0])
    a=""
    if prediction[0]==0:
        a+="NO SEPSIS"
    else:
        a+="SEPSIS"
    global username,age,mainsyptoms,address
    list1 = [username,age,address,mainsyptoms,a]
    with open("users.csv", "a", newline='') as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(list1)
    return render_template('result.html', prediction_text='{}'.format(prediction[0]),values=zip(column_names,features),result=prediction[0])

@app.route('/smartpredict',methods=['POST','GET'])
def smartpredict():
    global flag
    if(flag == False):
          return redirect(url_for('login'))
    features = [x for x in request.form.values()]
    custom_array = features[:7]
    for i in range(1,27):
        custom_array.append(0)
    for f in features[7:]:
        custom_array.append(f)
    print(custom_array)
    final_features = [np.array(custom_array)]    
    column_names=['HR','O2Sat','Temp','SBP','MAP','DBP','Resp','EtCO2','BaseExcess','HCO3','FiO2','pH','PaCO2','SaO2','AST','BUN','Alkalinephos',
                  'Calcium','Chloride','Creatinine','Bilirubin_direct','Glucose','Lactate','Magnesium','Phosphate','Potassium','Bilirubin_total','TroponinI','Hct','Hgb','PTT','WBC','Fibrinogen','Platelets','Age','Gender','Unit1','Unit2','HospAdmTime','ICULOS']
    final_features=pd.DataFrame(final_features,columns=column_names)
    prediction= model.predict(final_features)
    #print(prediction[0])
    a=""
    if prediction[0]==0:
        a+="NO SEPSIS"
    else:
        a+="SEPSIS"
    global username,age,mainsyptoms,address
    list1 = [username,age,address,mainsyptoms,a]
    with open("users.csv", "a", newline='') as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(list1)
    return render_template('result.html', prediction_text='{}'.format(prediction[0]),values=zip(column_names,features),result=prediction[0])

import json
@app.route('/getuserdetails')
def getuserdetails():
    with open("users.csv", 'r') as csvfile:
        datareader = csv.reader(csvfile)
        list_user = []
        for row in datareader:
            list_user.append({"name":row[0],"age":row[1],"address":row[2],"symptoms":row[3],"prediction":row[4]})
    response = app.response_class(
        response=json.dumps(list_user),
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
	app.run()
