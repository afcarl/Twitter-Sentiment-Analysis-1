# Feature Extractor
# 
# Features:
#   - [0] = # Chars/ # Words
#   - [1] = Question marks (?)
#   - [2] = Exclamation marks (!)
#   - [3] = Pronouns { i, me, we, us, you, he, him, she, her, it, they, them}
#   - [4] = Smile :) :D XD
#   - [5] = Sad :( :< :/
#   - [6] = URL (https:// or http:// or www. or .com or .gov or .edu .io .org)
#   - [7] = # of Ellipsis
#   - [8] = # of Hashtags

import csv
import random
import pickle
from collections import Counter
import time

import numpy
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence

from stop_words import get_stop_words
stop_words = get_stop_words("en")


random.seed(1) #time.time())

#BAD = 0 | GODD = 1

def create_vocab():

    good_dict = Counter()
    bad_dict = Counter()

    filename = "Sentiment Analysis Dataset.csv"

    seen = 0

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        seen += 1
        
        for line in reader:
            seen += 1
            sentiment = line[1]
            tweet = line[3]
            stweet = tweet.split()
            #print tweet.split()
            for word in stweet:
                if word != "":
                    if (sentiment == "0"):
                        bad_dict[word] += 1
                    else:
                        good_dict[word] += 1

            if (seen %10000 == 0): print seen,"---",sentiment,tweet

    with open("goddvocab.ser","wb") as f:
        pickle.dump(good_dict,f)

    with open("badvocab.ser","wb") as f:
        pickle.dump(bad_dict,f)

    print good_dict.most_common(10)
    print bad_dict.most_common(10)


def extract_features():
    global stop_words


    feat_num     = 8

    #Only choosing the best features (selected with WEKA)

    chwd         = 0
    exclamations = 1
    smile        = 2
    sad          = 3
    url          = 4
    ellipsis     = 5
    mention      = 6
    netprob      = 7
    #questions    = 8
    #pronoun      = 9
    #hashtags     = 10
    #capitals     = 11
    #length       = 12
    #test         = 13

    with open("goddvocab.ser","rb") as f:
        good_dict = pickle.load(f)

    with open("badvocab.ser","rb") as f:
        bad_dict = pickle.load(f)


    pronouns = ["i","me", "we", "us", "you", "he", "him", "she", "her", "it", "they", "them"]
    good_emoticons = [":)", ":D", "XD",":P", ":p", ";)",";D",";P"]
    bad_emoticons = [":(", ":S", ":'(", ">:(", ":/"]

    output = open("featured_dataset.csv","w+")
    filename = "Sentiment Analysis Dataset.csv"

    seen = 0

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        
        for line in reader:
            seen += 1
            sentiment = line[1]
            tweet = line[3]
            stweet = tweet.split()

            features = [0] * feat_num

            #11. Test - Feed the Sentiment
            #features[test] = sentiment

            #0. Char/Words
            features[chwd] = float(len(tweet))/len(stweet)

            #10. Length
            #features[length] = len(stweet)

            #12. Net Probability
            g = 0
            b = 0
            for word in stweet:
                #Removing stop words (for better percentage)
                #if word.lower() not in stop_words:
                #Don't include this. it did worse.
                g += good_dict[word]
                b += bad_dict[word]


            features[netprob] = float(g)/len(good_dict) - float(b)/len(bad_dict)


            for word in stweet:


                #1. Question Marks
                # if "?" in word:
                #     features[questions] += 1

                #2. Exclamation Marks
                if "!" in word:
                    features[exclamations] += 1

                #7. Ellipsis Marks
                if "..." in word:
                    features[ellipsis] += 1

                #6. URLs
                if "https://" in word.lower():
                    features[url] += 1
                elif "https://" in word.lower():
                    features[url] += 1
                elif "www." in word.lower():
                    features[url] += 1
                elif ".com" in word:
                    features[url] += 1

                #8. Hashtags
                # if word[0] == "#":
                #     features[hashtags] += 1
                if word[0] == "@":
                    features[mention] += 1

                #4. Good Emoticon
                if word in good_emoticons:
                    features[smile] += 1
                #5. Bad Emoticon
                elif word in bad_emoticons:
                    features[sad] += 1

                # #3. Pronouns
                #else:
                    # for p in pronouns:
                    #     if p == word.lower():
                    #         features[pronoun] += 1
                    #         break;
                #9. Capital Letters
                # for ch in word:
                #     features[capitals] += int(ch.isupper())

            #Save 
            towrite = sentiment

            for f in features:
                towrite += "," + str(f)

            output.write(towrite + "\n")
            if (seen %10000 == 0): print seen,"---",towrite

    output.close()


def create_batches(train_size=2000,test_size=2000,split=((0.5,0.5),(0.5,0.5))):

    X_train     = []
    y_train     = []
    train_good  = 0
    train_bad   = 0

    X_test     = []
    y_test     = []
    test_good  = 0
    test_bad   = 0

    with open("featured_dataset.csv", 'r') as f:
        reader = csv.reader(f)
        next(reader) #skip first line (labels)

        tr_good = False
        ts_good = False

        tr_bad = False
        ts_bad = False

        for line in reader:

            sentiment = line[0]
            tweet = line[1:]

            if (tr_good == ts_good == tr_bad == ts_bad == True): break;

            #Randomly drop some
            if (random.randint(0,1)):
                
                #Randomly drop into Train or Test set
                if (random.randint(0,1)):
                    if (int(sentiment) == 1): 
                        if (train_good >= train_size*split[0][1]): 
                            tr_good = True
                            continue;
                        train_good += 1
                    else: 
                        if (train_bad >= train_size*split[0][0]): 
                            tr_bad = True
                            continue;
                        train_bad += 1

                    X_train += [[float(i) for i in tweet]]
                    y_train += [int(sentiment)]


                else:

                    if (int(sentiment) == 1): 
                        if (test_good >= test_size*split[1][1]): 
                            ts_good = True
                            continue;
                        test_good += 1
                    else: 
                        if (test_bad >= test_size*split[1][0]): 
                            ts_bad = True
                            continue;
                        test_bad += 1

                    X_test += [[float(i) for i in tweet]]
                    y_test += [int(sentiment)]


    #print (train_bad,train_good,test_bad,test_good,train_size,test_size)

    #print len(X_train), len(y_train)
    #print len(X_test), len(y_test)
    #Serialize
    with open("train.ser","wb") as f:
        pickle.dump((X_train,y_train),f)

    with open("test.ser","wb") as f:
        pickle.dump((X_test,y_test),f)

    return (X_train,y_train,X_test,y_test)


def keras_nn(X_train,y_train,X_test,y_test,verbose=0,batchsize=1,layersize=250,epoch=1,hidden=1):

    #print numpy.asarray(X_train)[0:5]
    # create the model
    model = Sequential()
    #print X_train
    model.add(Dense(layersize, activation='relu',input_dim=len(X_train[0])))
    for h in range(1,hidden):
        model.add(Dense(layersize, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    if (verbose == 1):
        print(model.summary())


    # Fit the model

    #Batch Size: How many you are training at the same time.
    #
    model.fit(X_train, y_train, validation_data=(X_test, y_test), nb_epoch=epoch, batch_size=batchsize, verbose=verbose)
    # Final evaluation of the model
    score_test = model.evaluate(X_test, y_test, verbose=verbose)

    score_train = model.evaluate(X_train, y_train, verbose=verbose)

    if (verbose):
        print("Accuracy TEST: %.2f%%" % (score_test[1]*100))
        print("Accuracy TRAIN: %.2f%%" % (score_train[1]*100))

    return score_test[1]


###Experiments for Charts
# Batch Size
def exp_batchsize(low,high,i):
    print "Batchsize Experiment..."
    batchsize = low
    output = open("batchsize_exp","w+");

    (X_train,y_train,X_test,y_test) = create_batches(5000,2000,((0.5,0.5),(0.5,0.5)))
    while (batchsize <= high):

        result = keras_nn(X_train,y_train,X_test,y_test,batchsize=batchsize)
        
        output.write(str(batchsize)+" "+str(result)+"\n")
        print batchsize, result;
        batchsize += i
    
    output.close()

# Num of Hidden Layers
def exp_numhidden(low,high,i):
    print "Number of Hidden Layers Experiment..."
    hidden = low
    output = open("numhidden_exp","w+");

    (X_train,y_train,X_test,y_test) = create_batches(5000,2000,((0.5,0.5),(0.5,0.5)))
    while (hidden <= high):
        result = keras_nn(X_train,y_train,X_test,y_test,hidden=hidden)
        output.write(str(hidden)+" "+str(result)+"\n")
        print hidden, result;
        hidden += i
    output.close()


# Size of Hidden Layer
def exp_sizehidden(low,high,i):
    print "Size of Hidden Layer Experiment..."
    layersize = low
    output = open("sizehidden_exp","w+");

    (X_train,y_train,X_test,y_test) = create_batches(5000,2000,((0.5,0.5),(0.5,0.5)))
    while (layersize <= high):
        result = keras_nn(X_train,y_train,X_test,y_test,layersize=layersize)
        output.write(str(layersize)+" "+str(result)+"\n")
        print layersize, result;
        layersize += i
    output.close()

# Epoch
def exp_epoch(low,high,i):
    print "Epoch Experiment..."
    epoch = low
    output = open("epoch_exp","w+");

    (X_train,y_train,X_test,y_test) = create_batches(5000,2000,((0.5,0.5),(0.5,0.5)))
    while (epoch <= high):
        result = keras_nn(X_train,y_train,X_test,y_test,epoch=epoch)
        output.write(str(epoch)+" "+str(result)+"\n")
        print epoch, result;
        epoch += i
    output.close()





if __name__ == "__main__":
    #PART 1. CREATE THE GOOD AND BAD VOCABULARY DICTIONARIES (ONLY NEED TO DO IT ONCE)
    #print "\n\n>>Creating Vocab...\n\n"
    #create_vocab()

    #PART 2. EXTRACT FEATURES: TURN TWEET DATAPOINTS INTO A VECTOR OF FEATURES
    #print "\n\n>>Extracting Features...\n\n"
    #extract_features();

    #PART 3. CREATE BATCHES: SIMPLY GENERATE RANDOM BATCHES TO TEST WITH
    #print "\n\n>>Creating Batches...\n\n"


                                                           #  Train       Test
                                                           #(Good,Bad),(Good,Bad)
    #(X_train,y_train,X_test,y_test) = create_batches(2000,500,((0.5,0.5),(0.5,0.5)))

    #PART 4. ACTUALLY RUN OUR TEST ON A NEURAL NETWORK
    #print "\n\n>>Running Through Keras NN...\n\n"
    #keras_nn(X_train,y_train,X_test,y_test)

    #Experiments:
    exp_batchsize(1,2201,50)

    exp_numhidden(1,10,1)

    exp_sizehidden(100,1000,50)

    exp_epoch(1,10,1)