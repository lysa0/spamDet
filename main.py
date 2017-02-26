import urllib
import urllib.request
from queue import *
import codecs
from string import ascii_letters
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
import re
from sklearn.cluster import DBSCAN
from tkinter import *
from sklearn.neighbors import KNeighborsClassifier
vkcom="https://vk.com"
eps=1.2
minSmpl=2
commOfPost=220
commOfPostTrain=200
commofPostTest=10
vkids=["versusbattleru","mudakoff","durov"]
vkid=vkids[2]



def getData(site, fTrain, fTest, it):
    with urllib.request.urlopen(site) as url:
        cont = str(url.read(), encoding='utf-8')
    url.close()
    #print(site)
    #print(cont)
    nextPage=""
    nextPage=cont[cont.find("\"show_more_wrap\">")+45:cont.find("comments\">Показать")+8]
    qu=Queue()
    cont=cont[cont.find("<a id=\"comments\" name=\"comments\"></a>"):]
    comms=[]
    while(cont):
        cont=cont[cont.find("pi_author\" href=")+18:]
        author=cont[:cont.find("\">")]+' '
        cont=cont[cont.find("<div class=\"pi_text\">"):]
        comment=cont[cont.find("text\">")+6:cont.find("</div")]
        comment = removeTrash(comment)
        #comment = parsString(removeTrash(comment))
        if (comment!=""):
            comms.append(author+comment)
        cont=cont[1:]
    while(comms):
        comm=comms.pop()
        if (it<commofPostTest):
            fTest.write(comm+'\n')
        else:
            fTrain.write(comm+'\n')
        it+=1
        if (it==commOfPost):
            return
    if (nextPage!=""):
        site=vkcom+'/'+nextPage
        getData(site, fTrain, fTest, it)
def removeTrash(comment):
    newComment=""
    openBkt=False
    openSc=False
    for i in range (len(comment)):
        if (comment[i]=='<'):
            openBkt=True
        if (comment[i]=='&'):
            openSc=True
        if (not (openBkt or openSc)):
            if (comment[i]=='.' or comment[i]=='/'):
                newComment+=' '
            else:
                newComment+=comment[i]
        if (comment[i]=='>'):
            openBkt=False
            newComment+=' '
        if (comment[i]==';'):
            openSc=False
            newComment+=' '

    return newComment
def parsString(s):
        resS=""
        tmpS=""
        s=s.lower()
        for ch in s:
            if (ch in ascii_letters):
                tmpS+=ch
            else:
                #resS+=tmpS
                #tmpS=ch
                if (tmpS!=""):
                    resS+=' '
                    resS+=tmpS
                else:
                    resS+=' '
                    resS+=ch
                tmpS=""
        if tmpS=="":
            resS+=tmpS
        #print(resS)
        return resS



def makeDataset(site, fTrain, fTest):
    #print(site)
    with urllib.request.urlopen(site) as url:
        cont = str(url.read(), encoding='utf-8')
    url.close()
    '''
    nextPage=cont[cont.find("<a class=\"show_more\" href=\"")+28:cont.find("#posts\">Показать ещё")]
    print(nextPage)
    '''
    #print(cont)
    qu=Queue()
    while(cont):
        #cont=cont[cont.find("href=\"/wall"):]
        cont=cont[cont.find("wi_date\" href=\"/wall"):]
        post=cont[15:cont.find("\"", 16)]
        #print(post)
        if (post!=""):
            qu.put(post)
        cont=cont[1:]
    it=0
    while(not qu.empty()):
        getData(str(vkcom+qu.get()),fTrain, fTest, it)
    '''
    if (nextPage!=""):
        site=vkcom+'/'+nextPage
        makeDataset(site)
    '''

def readDataset():
    fT=open('datasetTrain', 'r')
    vectorsSTrain=[]
    for i in fT:
        vectorsSTrain.append(i)
    fT.close()
    f=open('dataset', 'r')
    vectorsS=[]
    for i in f:
        vectorsS.append(i)
    f.close()
    return vectorsSTrain, vectorsS


def train(datasetTrain, dataset):
    # Obtain some string samples.http://localhost:8888/notebooks/p/py/Untitled%20Folder/main.ipynb#
    # Get a char-based vectorizer with (1,2) n-gram range.
    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2))
    # Vectorize the samples.
    vectors = vectorizer.fit_transform(datasetTrain)
    vectorizer1 = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), vocabulary=vectorizer.vocabulary_)
    # Vectorize the samples.
    vectors1 = vectorizer1.fit_transform(dataset)
    #print(vectorizer.get_feature_names())
    #print(vectors)
    return vectors, vectors1

def clusterization(vectors):
    model = DBSCAN(eps=eps, min_samples=minSmpl).fit(vectors)
    return model



def make(id):
    site=vkcom+'/'+id+'?offset=50&own=1'
    fTrain=open('datasetTrain', 'w')
    fTest=open('dataset', 'w')
    makeDataset(site,  fTrain, fTest)
    fTrain.close()
    fTest.close()


'''
def action(event):
    ent.delete("1.0", END)
    ent.insert("1.0", check(tf.get("1.0",END)))
root = Tk()
tf=Text(root, height=8, width=70)
tf.pack()
ent = Text(root,height=1,width=3)
ent.pack()
but = Button(root)
but["text"]="Check"

but.bind("<Button-1>", action)
but.pack()
root.mainloop()
'''
#makeDataset()
#print(vectorsString)
#vectors=train(vectorsString)
#print(vectors)
#model = clusterization(vectors)
make(vkid)
vectorsStringTrain,vectorsString=readDataset()
vectors,vectors1=train(vectorsStringTrain, vectorsString)
model=clusterization(vectors)
neigh = KNeighborsClassifier(n_neighbors=2)
labels=[]
for i in range (len(model.labels_)):
    if (model.labels_[i]==-1):
        labels.append("OK")
    else:
        labels.append("SPAM")
neigh.fit(vectors, labels)
#print(vectors.shape[1],vectors1.shape[1])
resTest = neigh.predict(vectors1)
for i in range(len(vectorsString)):
    print(resTest[i], vectorsString[i])
print(len(set(model.labels_)))
for j in range (len(set(model.labels_))):
    print ( "!!!!!!!!!!!!!!", j-1, "!!!!!!!!!!!!!!")
    for i in range(len(vectorsStringTrain)):
        if (model.labels_[i]==j-1):
            print(vectorsStringTrain[i])
