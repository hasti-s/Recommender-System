import nltk
import pymysql as mysql
from stemming.porter2 import stem
import re
import csv

#nltk.download('punkt')
db = mysql.connect(host="127.0.0.1", password="", user="root", db="BSCTH", charset='utf8', use_unicode=True)
cursor = db.cursor()

query = "SELECT `title` FROM `articles`"
cursor.execute(query)
stopWords = []
file_stopWords = open("stopWords.txt")
stopWords = file_stopWords.readlines()
stopWords = [x.strip() for x in stopWords]

tokens = []
for i in range(0, cursor.rowcount): #cursor.rowcount
    result = cursor.fetchone()
    string = result[0]
    string = re.sub('[^\d\w\s\-_]','',string)
    tokens.extend(stem(word) for word in string.split())


final_tokens = [x for x in tokens if x not in stopWords]
final_tokens = list(set(final_tokens))

print(len(final_tokens))

file = open("finalTokens.txt", "w")
for item in final_tokens:
  file.write("%s\n" % item)


cursor.execute(query);
rows = []

for i in range(0, cursor.rowcount): #cursor.rowcount
    result = cursor.fetchone()
    string = result[0]
    string = re.sub('[^\d\w\s\-_]','',string)
    rows = [stem(word) for word in string.split()]
    print(i)
    vector = []
    for j in range(0, len(final_tokens)):
        if final_tokens[j] in rows:
            vector.append(j)
        # else:
        #     vector.append("0")
    #print(vector)
    with open('vectors_new.csv', 'a') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(vector)


cursor.close()
db.close()

