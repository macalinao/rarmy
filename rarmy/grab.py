import requests
import json
from BeautifulSoup import BeautifulSoup

config = json.load(open('config/config.json'))

def danbooru(url):
    """
    Grabs an image from Danbooru and prepares it for upload to Reddit.
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    full_title = soup.title.string

    s1 = full_title.find('(')
    s2 = full_title.find(')')

    title = full_title[0:s1].strip().title()
    source = full_title[s1 + 1:s2].strip().title()
    reddit_title = title + ' [' + source + ']'
    reddit_comment = '[Source - Danbooru](' + url + ')'

    img = 'http://danbooru.donmai.us/' + soup.find(id='image')['src']

    headers = {'Authorization': 'Client-ID ' + config['imgur']['client_id']}
    payload = {
        'image': img,
        'title': title,
        'description': full_title
    }

    r = requests.post('https://api.imgur.com/3/image', headers=headers, data=payload)
    link = r.json()['data']['link']

    return {
        'title': reddit_title,
        'comment': reddit_comment,
        'link': link
    }
