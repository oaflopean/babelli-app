import json

ids = json.load(open("ids"))

links = json.load(open("Babelli.json"))
string=""



ksitemap = open("sitemap.1.txt", mode="w")
gsitemap= open("sitemap.2.txt", mode="w")


for links in ids.keys()[0:25000]:
    string =  "http://babelli-gutenberg-copypasta.appspot.com/page/"+links+"\n"

    ksitemap.write(string)

for links in ids.keys()[25001:]:
    string =  "http://babelli-gutenberg-copypasta.appspot.com/page/"+links+"\n"
    gsitemap.write(string)



ksitemap.close()
gsitemap.close()



