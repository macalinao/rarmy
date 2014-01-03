from lib import army
import requests
from BeautifulSoup import BeautifulSoup
import json

config = json.load(open('config/config.json'))

def danbooru_grab(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    full_title = soup.title.string

    s1 = full_title.find('(')
    s2 = full_title.find(')')

    title = full_title[0:s1].strip().title()
    source = full_title[s1 + 1:s2].strip().title()
    reddit_title = title + ' [' + source + ']'
    reddit_comment = '[Source - Danbooru](' + url + ')'

    img = 'http://danbooru.donmai.us/' + soup.find(alt='Sample')['src']

    headers = {'Authorization': 'Client-ID ' + config['imgur']['client_id']}
    payload = {
        'image': img,
        'title': title,
        'description': full_title
    }

    r = requests.post('https://api.imgur.com/3/image', headers=headers, data=payload)
    link = r.json()['data']['link']

    return {
        'reddit_title': reddit_title,
        'reddit_comment': reddit_comment,
        'link': link
    }

post = danbooru_grab('http://danbooru.donmai.us/posts/1583318')

# s = army.Soldier({ 'user': 'SelfishArithmetic', 'pass': '--censored from git--' })
# s.login('46.249.66.50:8080')
# s.vote('t3_1ubfuy')
