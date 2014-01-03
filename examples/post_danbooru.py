from rarmy.grab import danbooru
from rarmy.data import captchas
from rarmy import Army

url = raw_input('Enter a Danbooru url: ')
post = danbooru(url)

army = Army(5) # Make an army of 5 users
s = army.random_soldier()
post = s.submit(post['title'], 'awwnime', captchas.pop(), url=post['link'])

print post
