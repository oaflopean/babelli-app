import csv
import json

import requests


def exists(site, path):
    request = requests.get(site+path)

    if request.status_code == 200:
        return True
    else:
        return False


site="https://storage.googleapis.com/"
x = json.load(open('Gutenberg.json'))

f = csv.writer(open("babellihttp.csv", "w"))

# Write CSV Header, If you dont need that, remove this line
f.writerow(["title", "author", "bookid", "subjects"])

for book in sorted(x.keys()):
    print("checking "+str(x[book]["id"]))
    if exists(site,"babelli-epubs/text/"+str(x[book]["id"])+".txt"):
        print(str(x[book]["id"])+" exists as text!")
        try:
            author = x[book]["author"].split(", ")
        except AttributeError:
            author = "None"
        try:
            author = author[1] + " " + author[0]
        except IndexError:
            author = x[book]["author"]
        f.writerow([str(x[book]["title"]), str(author), str(x[book]["id"]), " ".join(x[book]["subjects"])])

    elif exists(site, "babelli-epubs/epub/pg"+str(x[book]["id"])+"-images.epub"):
        print(str(x[book]["id"])+" exists as EPUB!")

        try:
            author = x[book]["author"].split(", ")
        except AttributeError:
            author = "None"
        try:
            author = author[1] + " " + author[0]
        except IndexError:
            author = x[book]["author"]
        f.writerow([str(x[book]["title"]), str(author), str(x[book]["id"]), " ".join(x[book]["subjects"])])


    else:
        print("does not exist!")
        continue
