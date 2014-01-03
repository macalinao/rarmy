from ..lib import army

url = raw_input('Enter a Reddit post to mass-upvote: ')

a = army.Army(size=5)
a.upvote_submission(url)

print 'Check the post; it should have +5 upvotes.'
