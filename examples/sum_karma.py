from rarmy import Army

army = Army(25)
lk = 0
ck = 0
for s in army.soldiers:
    try:
        me = s.me()['data']
        lk += me['link_karma']
        ck += me['comment_karma']
    except:
        print 'Error %s' % s.acct['user']

print 'Link: %d     Comment: %d     Total: %d' % (lk, ck, lk + ck)