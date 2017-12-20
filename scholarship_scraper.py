from bs4 import BeautifulSoup
from requests import get
import pandas as pd
from time import sleep
from random import randrange
import sqlalchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import re

# start

# create max entries to main site

faculty = []
scholarship = []
state = []
total_value = []
link = []
missed = []

for tag in [['merit-academic-achievement', 'content_container_667807'], ['equity', 'content_container_667817'],
            ['merit-equity', 'content_container_667828'], ['indigenous', 'content_container_667838'],
            ['graduate-scholarships', 'content_container_667854'], ['international', 'content_container_667868'],
            ['accommodation', 'content_container_667905'], ['travel-placement', 'content_container_667930']]:
    sleep(randrange(1, 4))
    url = 'http://www.monash.edu/students/scholarships/current/' + tag[0]
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    n = soup.find('div', id=tag[1])
    t = n.find_all('li')
    response.close()

    for item in t:
        word = item.find_parent().find_previous().text
        if "Art" in word:
            faculty.append("Arts")
        else:
            faculty.append(word)
        scholarship.append(item.a.text)
        # check for leadership
        if 'Leadership' in item.a.text:
            state.append('Leadership')
        else:
            state.append(tag[0])
        link.append(item.a.get('href'))
        # Now we access total value
        try:
            response = get(link[-1])
        except:
            faculty.pop()
            missed.append(scholarship[-1])
            scholarship.pop()
            state.pop()
            link.pop()
            # skip loop
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('p', text='Total scholarship value') is not None:
            test = soup.find('p', text='Total scholarship value').find_next().text.replace(' ', '')
            test = test.replace(',', '')
            if re.findall('\d+', test) != []:
                total_value.append(int(re.findall('\d+', test)[0]))
            else:
                # delete entries
                faculty.pop()
                missed.append(scholarship[-1])
                scholarship.pop()
                state.pop()
                link.pop()

        elif soup.find('strong', text='Benefits') is not None:
            test = soup.find('strong', text='Benefits').find_next().text.replace(' ', '')
            test = test.replace(',', '')
            if re.findall('\d+', test) != []:
                total_value.append(int(re.findall('\d+', test)[0]))
            # Now check again
            else:
                # delete entries
                faculty.pop()
                missed.append(scholarship[-1])
                scholarship.pop()
                state.pop()
                link.pop()

        else:
            # delete entries
            faculty.pop()
            missed.append(scholarship[-1])
            scholarship.pop()
            state.pop()
            link.pop()
        response.close()
        sleep(1)
    print('1 done')

# open database connection
app = Flask(__name__)
app.secret_key = "sjfgiefyhube"
DB_URL = 'mysql://{user}:{pw}@{url}/{db}'.format(user='root', pw='root', url='localhost',
                                                 db='students')

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'scholarships'
    scholarships = db.Column(db.String(200), unique=True, nullable=False, primary_key=True)
    faculty = db.Column(db.String(100), unique=False, nullable=False)
    link = db.Column(db.String(1000), unique=False, nullable=False)
    state = db.Column(db.String(100), unique=False, nullable=False)
    total_value = db.Column(db.Integer, unique=False, nullable=False)


db.create_all()
pd.set_option('display.max_colwidth', 1000)
pd.DataFrame(
    {'scholarships': scholarship, 'faculty': faculty, 'link': link, 'state': state,
     'total_value': total_value}).drop_duplicates(['scholarships'], keep='first').to_sql(
    name='scholarships', con=db.engine, if_exists="replace", index=False)





