from flask import Flask
from Query import search
from flask import request

app = Flask(__name__)

@app.route('/',methods=['POST'])
def hello():
    print(request.form['fName'][:1])
    return str(search(request.form['article'],request.form['fName'][:1]+' '+request.form['lName']))
