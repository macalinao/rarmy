from rarmy import Army, data
import requests

army = Army(15)
users = [ a['user'] for a in data.accts ]
posts = [ post['data'] for post in requests.get('http://www.reddit.com/r/awwnime/new/.json').json()['data']['children'] ]
for post in posts:
    if not post['author'] in users:
        print 'Downvoting %s.' % post['name']
        army.vote(post['id'], 3, -1)
