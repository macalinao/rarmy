from rarmy.grab import danbooru
from rarmy.data import captchas
from rarmy import Army

url = raw_input('Enter a Danbooru url: ')
votes = int(raw_input('Enter number of desired upvotes: '))

print 'Uploading image from Danbooru...'
img = danbooru(url)
print 'Image uploaded at ' + img['link']

print 'Creating army of ' + str(votes) + '...'
army = Army(votes) # Make an army

s = army.random_soldier()
print 'Posting on random soldier ' + s.acct['user']
post = s.submit(img['title'], 'awwnime', captchas.pop(), url=img['link'])
print 'Post created! ' + post['id']

print 'Posting comment showing source...'
comment = s.comment(post['name'], img['comment'])
print 'Comment posted! ' + comment['things'][0]['id']

print 'Mass upvoting...'
army.vote(post['id'])
print 'Upvoting complete.'
