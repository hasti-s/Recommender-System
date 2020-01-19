import collections
from stemming.porter2 import stem
import re
import csv
from operator import itemgetter
import pymysql as mysql
import json
import networkx as nx
import matplotlib.pyplot as plt
from operator import truediv


def search(query, scholar_name):
    file_stopWords = open("stopWords.txt")
    stopWords = file_stopWords.readlines()
    stopWords = [x.strip() for x in stopWords]
    query_t = []
    string = query
    string = re.sub('[^\d\w\s\-_]','',string)
    query_t.extend(stem(word) for word in string.split())
    query_t = [x for x in query_t if x not in stopWords]
    query_t = list(set(query_t))
    #print(query_t)

    with open("finalTokens.txt") as f:
        tokens = f.readlines()
    tokens = [x.strip() for x in tokens]

    #print(tokens[5988])
    vector_q = []
    for j in range(0, len(tokens)):
        if tokens[j] in query_t:
            vector_q.append(str(j))
    #print(vector_q)

    check = []
    with open('vectors_new.csv', 'r') as f:
      reader = csv.reader(f)
      for row in reader:
          check.append(row)

    distance = []
    for vector in check:
        intersection = len(set(vector_q).intersection(set(vector)))
        union = len(set().union(vector_q, vector))
        #print(union)
        distance.append(1 - (intersection/union))
    print(min(distance))
    final_dis = []
    for i in range(0, len(distance)):
        if distance[i] > 0 and distance[i] < 1:
            final_dis.append({"id": i, "distance": distance[i]})

    #sorted_dis = final_dis.sort(key=operator.itemgetter("distance"))

    # sorted_dis = [(dic["distance"], dic) for dic in final_dis]
    # sorted_dis.sort()
    # result = [dic for (key, dic) in sorted_dis]
    if len(final_dis) == 0:
        best_judge = ".متاسفانه برای این مقاله داوری یافت نشد"
        sent_data = {}
        sent_data['best_judge'] = best_judge
        sent_data['url'] = "https://scholar.google.com/citations?view_op=new_profile&hl=en"
        json_data = json.dumps(sent_data)
        return json_data


    result_sort = sorted(final_dis, key=itemgetter("distance"))

    pr = [x['distance'] for x in result_sort]
    #print(min(pr))

    db = mysql.connect(host="127.0.0.1", password="", user="root", db="BSCTH", charset='utf8', use_unicode=True)
    cursor = db.cursor()
    my_articles = []
    query = "SELECT `article_id` FROM `scholars` where `name` = \'" + str(scholar_name) + "\'"
    #print(query)
    cursor.execute(query)

    for i in range(0, cursor.rowcount):
        result = cursor.fetchone()
        my_articles.append(result[0])

    res_articles = []
    if len(result_sort) > 10:
        si = 10
    else:
        si = len(result_sort)
    for i in range(0, si):
        #print(result_sort[i])
        if result_sort[i]["id"] + 2 not in my_articles:
            #print("!#@#@#%#^")
            res_articles.append(result_sort[i]["id"] + 2)

    judges = []
    for i in range(0, len(res_articles)):
        query = "SELECT `name` FROM `scholars` where `article_id` = "
        query += str(res_articles[i])
        #print("******" + query)
        cursor.execute(query)
        for j in range(0, cursor.rowcount):
            result = cursor.fetchone()
            judges.append(result[0])


    ##########################################################Graph-one-time
    # G = nx.Graph()
    # nodes = []
    # query = "SELECT DISTINCT `name` FROM `scholars`"
    # cursor.execute(query)
    # for j in range(0, cursor.rowcount):
    #     result = cursor.fetchone()
    #     nodes.append(result[0])
    # G.add_nodes_from(nodes)
    #
    # for c in range(2, 23052):
    #     query = "SELECT DISTINCT `name` FROM `scholars` WHERE `article_id` = " + str(c)
    #     print("query$&%&%^&: " + query)
    #     cursor.execute(query)
    #     authors = []
    #     for j in range(0, cursor.rowcount):
    #         result = cursor.fetchone()
    #         authors.append(result[0])
    #     is_edge = 0
    #     for a in range(0, len(authors)):
    #         for b in range(a, len(authors)):
    #             if authors[a] == authors[b]:
    #                 continue
    #             for (u, v, wt) in G.edges.data('weight'):
    #                 if u == authors[a] and v in authors[b]:
    #                     G[u][v]['weight'] += 1
    #                     is_edge = 1
    #                     break
    #             if is_edge == 0:
    #                 G.add_edge(authors[a], authors[b], weight=1)
    # # plt.subplot(121)
    # # nx.draw(G, with_labels=True, font_weight='bold')
    # # plt.show()
    # file = open("nodes.txt", "w")
    # file.write(str(G.nodes()))
    # file = open("edges.txt", "w")
    # file.write(str(list(G.edges.data('weight'))))
    # print("nodes: ")
    # print(str(G.nodes()))
    # print("edges: ")
    # print(str(list(G.edges.data('weight'))))

    G = nx.Graph()
    with open('nodes.txt', 'r') as myfile:
        nodes_s = myfile.read().replace(', \'', '')
    nodes = nodes_s.split('\'')
    G.add_nodes_from(nodes)

    with open('edges.txt', 'r') as myfile:
        edges_s = myfile.read().replace('), ', '')
    edges = edges_s.split('(')
    # print("these are the edges:")
    # print(edges)
    for edge in edges:
        det = edge.split(', ')
        if len(det) == 3:
            G.add_edge(str(det[0].replace('\"', '').replace('\'', '')), str(det[1].replace('\"', '').replace('\'', '')), weight=int(det[2]))
    #if(scholar_name in nodes):


    counter = collections.Counter(judges)
    # sorted_judges = sorted(judges, key=counts.get, reverse=True)
    fr = counter.values()
    judges = list(set(judges))

    weighted_distance = []
    for judge in judges:
        if (scholar_name in nodes and nx.has_path(G, source=scholar_name, target=judge)):
            path = nx.shortest_path(G, source=scholar_name, target=judge, weight='weight')
            tot_weight = 0
            print("path:")
            print(path)
            for h in range(0, len(path) - 1):
                tot_weight += (G[str(path[h])][str(path[h + 1])]['weight'])
                print(G[str(path[h])][str(path[h + 1])]['weight'])

            z = tot_weight/(len(path)-1)
            weighted_distance.append(z/len(path))
            print("check")
            print(tot_weight)
            print(len(path))
            print("weight:")
            print(z/len(path))
        else:
            weighted_distance.append(1)

    score = list(map(truediv, fr, weighted_distance))
    print(score)
    print(fr)
    print(judges)
    #counts = Counter(judges)
    temp = len(judges)
    best_judge = None
    found = 0
    link = "/citations?view_op=new_profile&hl=en"
    for q in range(0, temp):
        best_judge = judges[score.index(max(score))]
            #str(max(judges, key=(judges.count/weighted_distance[judges.index(max(judges, key=judges.count))])))
        fl_names = best_judge.split()
        print(fl_names)
        print(type(fl_names))
        with open("data.txt") as f:
            content = f.readlines()
            for line in content:
                name_part = line.split(";;")[0]
                last_name = name_part.split()[len(name_part.split())-1]
                first_name = name_part.split()[0]
                if last_name == fl_names[1] and first_name[:1] == fl_names[0][:1]:
                    best_judge = first_name + ' ' + last_name
                    link = line.split(";;")[1]
                    found = 1
                    break
            if found == 1:
                break
            else:
                judges.remove(max(judges, key=judges.count))
                continue

    cursor.close()
    db.close()
    if best_judge == None:
       best_judge = ".متاسفانه برای این مقاله داوری یافت نشد"
    print(best_judge)
    sent_data = {}
    sent_data['best_judge'] = best_judge
    sent_data['url'] = "https://scholar.google.com" + link
    json_data = json.dumps(sent_data)
    print(json_data)
    return json_data
















