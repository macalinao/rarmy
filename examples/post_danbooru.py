from rarmy.grab import danbooru
from rarmy.data import captchas
from rarmy import Army

url = raw_input('Enter a Danbooru url: ')
votes = int(raw_input('Enter number of desired upvotes: '))

print 'Creating army of ' + str(votes) + '...'
army = Army(votes) # Make an army

print 'Uploading image from Danbooru...'
img = danbooru(url)
print 'Image uploaded at ' + img['link']

s = army.random_soldier()
print 'Posting on random soldier ' + s.acct['user']

count = 0
while True:
    if count > 5:
        s = army.random_soldier()
        print 'Could not post, changing to soldier ' + s.acct['user']
        count = 0

    post = s.submit(img['title'], 'awwnime', captchas.next()[0], url=img['link'])
    if not post:
        print 'Error posting, retrying...'
        count += 1
    else:
        break
print 'Post created! ' + post['id']

print 'Posting comment showing source...'
comment = s.comment(post['name'], img['comment'])
print 'Comment posted! ' + comment['id']

print 'Mass upvoting...'
army.vote(post['id'])
print 'Upvoting complete.'
