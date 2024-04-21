from http.client import responses
import nltk
#nltk.download('punkt')#
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
from tensorflow.python.framework import ops
import random
import json
import pickle
import mysql.connector

with open("intents.json") as file:
    data = json.load(file)

try:
    with open("data.pickle" , "rb") as f:
        words , labels , training , output = pickle.load(f)
    
except:

    words = []
    labels =[]
    doc_x = []
    doc_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrd = nltk.word_tokenize(pattern)
            words.extend(wrd)
            doc_x.append(wrd)
            doc_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])
            

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))
    

    labels = sorted(labels)
    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x ,docs in enumerate(doc_x):
        bag = []
        wrd = [stemmer.stem(w.lower()) for w in docs]
        for w in words:
            if w in wrd:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(doc_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)
   
    with open("data.pickle" , "wb") as f:
        pickle.dump((words , labels , training , output) , f)



    ##tensorflow.reset_default_graph()

net = tflearn.input_data(shape = [None , len(training[0])])
net = tflearn.fully_connected(net , 8)
net = tflearn.fully_connected(net , 8)
net = tflearn.fully_connected(net , len(output[0]), activation = "softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
try:
    model.load("model.tflearn")
except:   
    ops.reset_default_graph()
    net = tflearn.input_data(shape = [None , len(training[0])])
    net = tflearn.fully_connected(net , 8)
    net = tflearn.fully_connected(net , 8)
    net = tflearn.fully_connected(net , len(output[0]), activation = "softmax")
    net = tflearn.regression(net)

    model = tflearn.DNN(net)
    model.fit(training , output , n_epoch=1000 , batch_size=8 , show_metric = True)
    model.save("model.tflearn")

def bag_of_words(s , words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i , w in enumerate(words):
            if w==se:
                bag[i] =  1

    return numpy.array(bag)


class ChatBot:
    
    def __init__(self):
        pass
        
        
    def reply(self , message):
        results = model.predict([bag_of_words(message , words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]
      
        
        if results[results_index] > 0.7:
            
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']

            
            return [random.choice(responses) , tag]
        else:
            return "I didnt get that , try again"
        
    def sauces(self ,  whatsappNumber , message):
            invalidMessage = "I didnt get that , try again"
            db = mysql.connector.connect(
                host ="localhost",
                user = "root",
                passwd = "Andile@2001",
                database = "pos"

            )
            mycursor = db.cursor()
            mycursor.execute("SELECT order_num ,customer_number , sauces FROM orders")
            result_set = mycursor.fetchall()
            if message == "yes":
                yesToSauces = "with sauces"
                if len(result_set) == 0:
                    return str(invalidMessage)
                else:
                    feedback = "Thank you for ordering , your order has been taken , we will alert you when you can come collect"
                    for x in result_set:
                        y = list(x)
                        if y[1] == whatsappNumber and y[2] == None:
                            num = y[0]
                            mycursor.execute("UPDATE orders SET sauces = %s WHERE order_num = %s" , (yesToSauces ,  num))
                            db.commit()
                            return str(feedback)
            elif message == "no":
                noToSauces = "no"
                if len(result_set) == 0:
                    return str(invalidMessage)
                else:
                    for x in result_set:
                        y = list(x)
                        if y[1] == whatsappNumber and y[2] == None:
                            num = y[0]
                            mycursor.execute("UPDATE orders SET sauces = %s WHERE order_num = %s" , (noToSauces ,  num))
                            db.commit()
                            return str(feedback)
