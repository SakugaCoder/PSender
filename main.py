import requests
import bs4

import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
import time

import pandas as pd
import random
from datetime import datetime

import cv2
from skimage import io
import base64

email_sended = False
hour_to_send = 14

base_URL = 'https://urltoextractimages.com'
senders_csv_route = './sender_emails.csv'
targets_csv_route = './targets.csv'

targets_emails_df = pd.read_csv(targets_csv_route)
targets = []

for i,row in targets_emails_df.iterrows():
    targets.append(row['target'])

print('Targets: ')
print(targets)

school_subjects = ['Subject 1', 'Subject 2']
other_subjects = ['Subject 1','Subject 2']
last_email = ''
smtp_server = 'smtp.gmail.com'
port = 587

def getImgURI(img_url):
    image = io.imread(img_url)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    ts = datetime.timestamp(datetime.now())
    cv2.imwrite("{}.jpg".format(ts),image)
    encoded = base64.b64encode(open("{}.jpg".format(ts), "rb").read())
    encoded_str = str(encoded)
    
    return encoded_str[2:len(encoded_str)-1]


def sendEmail(img_url):
    img_URI = getImgURI(img_url)
    global last_email
    print('Sending email')
    #Getting email and password from csv
    #Get random number in order to get the credentials from that index

    sender_emails_df = pd.read_csv(senders_csv_route)
    sender_emails_size = sender_emails_df.shape[0]
    rand_index = random.randint(0,sender_emails_size - 1)
    
    sender_email = ''
    password = ''
    for i,row in sender_emails_df.iterrows():
        print(i)
        if i == rand_index:
            if len(last_email) > 0:
                if last_email != row['email']:
                    last_email = sender_email
                    sender_email = row['email']
                    password = row['passwd']
                    print(f"email: {sender_email}, passwd: {password}")
                    break
                else:
                    rand_index = random.randint(0,sender_emails_size - 1)
            else:
                sender_email = row['email']
                last_email = sender_email
                password = row['passwd']
                print(f"email: {sender_email}, passwd: {password}")
                break

    with smtplib.SMTP(smtp_server, port) as server:
        try:
            #server = smtplib.SMTP(smtp_server,port)
            #server.ehlo()
            server.starttls()
            server.login(sender_email,password)

            #Generateing subject
            if sender_email == "especial.email@mail.com":
                subject = school_subjects[random.randint(0,len(school_subjects) -1)]
            else:
                subject = other_subjects[random.randint(0,len(other_subjects) -1)]

            for target in targets:
                message = MIMEMultipart()
                message['Subject'] = subject
                message['From'] = sender_email
                

                html = """
                <p>{}</p>
                <a href="{}">Presiona para conocer mas</div>

                """.format(subject,img_url)
                print("It sends this html:")
                print(html)

                main_part = MIMEText(html,"html")

                message.attach(main_part)
                message['To'] = target
                server.sendmail(sender_email, target, message.as_string())
                time.sleep(10)

        except Exception as e:
            server.quit()
            print(e)


def init():
    request = requests.get(url = base_URL)
    soup = bs4.BeautifulSoup(request.text,'html.parser')

    images = soup.find_all('img',class_=['thumb','img-responsive'])
    print(images)
    rand_index = random.randint(0,len(images)-1)
    first_image_url = images[rand_index].get('src')
    print(f"First image: {first_image_url}")
    sendEmail(first_image_url)
    pass

def main():
    global email_sended
    last_day = (datetime.now()).day
    while(1):
        today = datetime.now()
        hour = today.hour
        day = today.day
        if day != last_day:
            last_day = day
            email_sended = False
        elif not email_sended:
            if hour_to_send == hour:
                init()
                email_sended = True
            else:
                print(today)
        #else:
            #print("Email has been sended for today :)")

if __name__ == '__main__':
    main()