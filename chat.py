from flask import Flask , request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from chatbot import ChatBot
import mysql.connector



account_sid = 'AC1c220a59cb525ff0722e87f4b647ef6e'
auth_token = '35523f3b41606e9c749c6872faaf2118'
client = Client(account_sid, auth_token)

chat = Flask(__name__)

@chat.route("/")
def hello():
    return "hello world"


@chat.route("/sms" , methods=["POST"])
def sms_reply():
    db = mysql.connector.connect(
        host ="localhost",
        user = "root",
        passwd = "Andile@2001",
        database = "pos"

     )
    mycursor = db.cursor()
    whatsappNumber = (request.form.get("From"))
    stringWhatsappNumber = whatsappNumber[-12:]
    print(stringWhatsappNumber)
    message = request.form.get('Body')
    resp = MessagingResponse()
    getMessage = ChatBot()      
   

    if message.lower() == "yes":
       resp.message(getMessage.sauces(stringWhatsappNumber , message))
       return str(resp)

    elif message.lower() == "no": 
        resp.message(getMessage.sauces(stringWhatsappNumber , message))
        return str(resp) 
    else:  
        tag = ["Small chips" , "medium chips" , "large chips" , "basic" , "silver" , "gold" , "platinum"]
        answer = getMessage.reply(message)
        result_set =""
        for l in tag:
            if answer[1] == l:  
                mycursor.execute("SELECT customer_number, sauces FROM orders")
                result_set = mycursor.fetchall()
                if len(result_set) >  0:
                     for y in result_set:
                        for f in y:
                            if f == None:
                                resp.message("Please finish your previous order before moving on to the second order")
                                return str(resp)       
        if answer[1] in tag:
            for x , y in enumerate(tag):
               if tag[x] == answer[1]:
                    print(x)
                    mycursor.execute("INSERT INTO orders(customer_number , order_description) values(%s , %s)",(stringWhatsappNumber, answer[1]))
                    db.commit()
                    resp.message(answer[0])
                    return str(resp)
        else:
            resp.message(answer[0])
            return str(resp)

@chat.route("/java" , methods=["POST"])
def handle_form_data():
    if request.method == 'POST':
        form_data = request.form
        print("Received Form Data:")
        for key, value in form_data.items():
            print(f"{key}: {value}")
        message = client.messages.create(
                                         from_='whatsapp:+14155238886',
                                         body='Your order is done , you can come collect',
                                         to=value
                                        )

        return 'Form data received successfully!'
    else:
        return 'Invalid request method'
        
        
   
 

if __name__ == "__main__":
    chat.run(debug = True)





         
