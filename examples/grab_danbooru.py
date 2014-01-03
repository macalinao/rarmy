from lib import army, grab

url = raw_input('Enter a Danbooru url: ')
post = grab.danbooru(url)

print post
