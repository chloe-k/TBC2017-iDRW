from bs4 import BeautifulSoup
import requests
from collections import defaultdict

hgnc = dict()
with open("mart_export.txt", "r") as inp:
    for line in inp.readlines()[1:]:
        #hgnc_id, hgnc_sym = line.strip().split()
        hgnc_sym, hgnc_id = line.strip().split()
        hgnc_id = int(hgnc_id)
        hgnc[hgnc_id] = hgnc_sym

def fetch(path):
    print "fetching {}".format(path)
    with open(path, "r") as inp:
        contents = inp.read()

    bs = BeautifulSoup(contents)
    gene = defaultdict(list)
    for entry in bs.find_all('entry'):
        if entry['type'] == "gene":
            for hsa_id in entry["name"].split():
                link = "http://www.genome.jp/dbget-bin/www_bget?{}".format(hsa_id)
                #print(link, )
                r = requests.get(link)
                #print(r.status_code)
                cur_bs = BeautifulSoup(r.text, "html5lib")
                for a in cur_bs.find_all('a'):
                    if a.has_key("href") and "genenames" in a["href"]:
                        gene[entry['id']].append(a.text)


    gene_int = dict()
    for g in gene:
        gene_int[int(g)] = map(int, gene[g])


    edges = []
    for link in bs.find_all("relation"):
        e1 = int(link["entry1"])
        e2 = int(link["entry2"])
        type = str(link["type"])
        if e1 in gene_int and e2 in gene_int:
            for g1 in gene_int[e1]:
                for g2 in gene_int[e2]:
                    edges.append("\t".join([hgnc[g1], hgnc[g2], type]))

    nodes = set()
    for n in gene_int:
        for x in gene_int[n]:
            nodes.add(hgnc[x])
    edges = sorted(list(set(edges)))

    with open(path.replace(".xml","_nodes.txt"), "w") as oup:
        print >> oup, "\n".join(sorted(nodes))

    with open(path.replace(".xml","_edges.txt"), "w") as oup:
        print >> oup, "\n".join(sorted(edges))
