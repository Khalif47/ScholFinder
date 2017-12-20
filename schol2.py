from bs4 import BeautifulSoup
from requests.sessions import HTTPAdapter, Session
from requests import get
import pandas as pd
from time import sleep
from random import randrange
import re

# start

# create max entries to main site
s = Session()
s.mount('/fees-scholarships/scholarships/find/international-student-scholarships/arts-merit',
        HTTPAdapter(max_retries=1000))

faculty = []
scholarship = []
state = []
total_value = []
link = []
missed = []

for tag in [['international', 'content_container_667868']]:
    sleep(randrange(1, 4))
    url = 'http://www.monash.edu/students/scholarships/current/' + tag[0]
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    n = soup.find('div', id=tag[1])
    t = n.find_all('li')
    response.close()

    for item in t:
        faculty.append(item.find_parent().find_previous().text)
        scholarship.append(item.a.text)
        # check for leadership
        if 'Leadership' in item.a.text:
            state.append('Leadership')
        else:
            state.append(tag)
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
                total_value.append(re.findall('\d+', test)[0])
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
                total_value.append(re.findall('\d+', test)[0])
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

table = pd.DataFrame({'scholarships': scholarship, 'faculty': faculty, 'link': link})
print(table)
