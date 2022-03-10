from flask import Flask,render_template,request,jsonify
import os
import json
from flask.helpers import flash, url_for
import shutil
from tika import parser
import spacy
from werkzeug.utils import redirect, secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf','xlsx','xls'}
UPLOAD_FOLDER = './static/temp'
app=Flask(__name__)
app.config['DEBUG']=True
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

#<--------------------Home------------------------>
@app.route('/')
def home():
    return render_template('upload.html')


#<--------------Folder Uploading....--------------->

@app.route('/fromfolder',methods=['GET','POST'])
def copyfilesfromfolder():    
    try:
        path=os.path.join(UPLOAD_FOLDER,'uploads')
        if os.path.exists(path):
            shutil.rmtree(path)
            os.mkdir(path)
        else:
            os.mkdir(path)
        dic=dict()
        inc=1
        if request.method=='POST':
            if request.files.getlist("folder"):
                files=request.files.getlist('folder')
                for file in files:
                    p=os.path.join(path,secure_filename(file.filename))
                    if os.path.exists(p):
                        continue
                    else:
                        dic[inc]=os.path.basename(secure_filename(file.filename))
                        inc=inc+1
                        file.save(os.path.join(path,secure_filename(file.filename)))    
            else:
                file=request.files["folder"]
                dic[inc]=os.path.basename(secure_filename(file.filename))
                file.save(os.path.join(path,secure_filename(file.filename)))    
            return render_template('output.html',dic=dic)
    except:
        return jsonify({'message':'Error Encountered!!!'})

#<-----------------single file/multiple files/zip file uploading----------------->
@app.route('/fromfiles',methods=['GET','POST'])
def copyfromfiles():
    try:
        path=os.path.join(UPLOAD_FOLDER,'uploads')
        if os.path.exists(path):
            shutil.rmtree(path)
            os.mkdir(path)
        else:
            os.mkdir(path)
        dic=dict()
        inc=1
        if request.method=='POST':
            files=request.files.getlist('file')
            for file in files:
                if file.filename.endswith('.zip'):
                    fol=file.filename.split('.')[0]
                    file.save(os.path.join(path,secure_filename(file.filename)))
                    tempath=os.path.join(path,secure_filename(file.filename))
                    shutil.unpack_archive(tempath,path)
                    src=os.path.join(path,fol)
                    shutil.move(src,path)
                    shutil.rmtree(src)
                    for file in os.scandir(path):
                        dic[inc]=os.path.basename(file.path)
                        inc=inc+1
                else:
                    file.save(os.path.join(path,secure_filename(file.filename)))
                    dic[inc]=os.path.basename(secure_filename(file.filename))
                    inc=inc+1
            return render_template('output.html',dic=dic)
    except:
        return jsonify({'':'Error Encountered'})


#<-----------------reading all files in the folder-------------------->
@app.route('/readallfiles',methods=['GET','POST'])
def read_all_files():
    try:
        if copy_path:
            print(copy_path)
            dic={}
            inc=1
            if os.path.exists(jsonpath):
                shutil.rmtree(jsonpath)
                os.mkdir(jsonpath)
            else:
                os.mkdir(jsonpath)
            for file in os.scandir(copy_path):
                d={}
                key=os.path.basename(file.path)
                jsonfile=os.path.splitext(key)[0]
                jsonfile=jsonfile+'.json'
                if file.path.endswith(".doc"):
                    data=parser.from_file(file.path)
                  
                elif file.path.endswith(".pdf"):
                    data=parser.from_file(file.path)
                else:
                    continue
                content=data['content']
                content=" ".join(content.split())
                d[key]=content
                dic[inc]=jsonfile
                inc=inc+1
                with open(os.path.join(jsonpath,jsonfile),'w') as f:
                    json.dump(d,f,indent=2)
            return render_template('jsonoutput.html',dic=dic) 
                
    except:
        return jsonify({'message':'Error Encountered!!!'})


#<---------------reading individual file------------------------>
@app.route('/readfile/<value>',methods=['GET','POST'])
def read_one_file(value):
    try:
        #getting the path of the file
        temppath=os.path.join(copy_path,value)
        if temppath:
            dic=dict()
            if temppath.endswith('.pdf') or temppath.endswith('.doc') or temppath.endswith('.docx'):
                data=parser.from_file(temppath)
                content=data['content']
                content=" ".join(content.split())
                dic[value]=content
            else:
                return jsonify({'message':'files supported are pdf,doc,docx'})
        return jsonify(dic)
    except:
        return 'Error Occured!!!'

#<-----------Extracting Information from json------------>
@app.route('/extract/<value>',methods=['GET','POST'])
def extract_entities(value):
    try:
        temppath=os.path.join(jsonpath,value)
        if os.path.exists(temppath):
            with open(temppath,'r') as f:
                data=json.load(f)
            data=dict(data)
            for val in data.values():
                d=val
            nlp=spacy.load("en_core_web_sm")
            doc=nlp(d)
            text=[]
            for ent in doc.ents:
                text.append(ent.text)
            keywords=""
            for i in text:
                keywords=i+" "
            return d
            
    except:
        return 'Error Occured!!!!!'

if __name__ == '__main__':
    #creating example folder to store the data
    copy_path=os.path.join(UPLOAD_FOLDER,'uploads')
    jsonpath=os.path.join(UPLOAD_FOLDER,'json')
    app.run()