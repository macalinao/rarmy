from rarmy import Army

name = raw_input('Enter a Reddit post to mass-upvote: ')
amt = raw_input('Enter the amount of upvotes desired: ')

a = Army(int(amt))
a.vote(name)

print 'Check the post; it should have +' + amt + ' upvotes.'
