###################
# LinkFixerBotSnr #
# # #  By WS  # # #
###################

import sys, os, re, time, argparse, getpass, praw, reddit, config

default = {

	'credentials': {
	
		'username': '',
		'password': '',
		
	},
	
	'limit': '',
	
}

config_name = 'config.json'
sub_regex = re.compile(' r/[A-Za-z0-9_]+')

def bootup():
	
	version = "1.1"
	
	banned = [
		'loans', 'nba', 'aww', 'subredditdrama', 'againstmensrights', 'australia', 'shitpoliticssays',
		'scotch', 'metacanada', 'news', 'nfl', 'breakingbad', 'theredpill', 'whatisthisthing', 'conspiratard',
		'comics', 'mls', 'twoxchromosomes', 'politics', 'badhistory', '49ers', 'yugioh', 'mac', 'science',
		'polticaldiscussion', 'photography,', 'srsgaming', 'europe', 'cringe', 'soccer', 'tatoos', 'wtf',
		'buildapc', 'funny', 'nascar', 'conspiracy', 'gaming', 'fitness', 'iama', 'mensrights', 'adviceanimals',
		'nottheonion', 'pics', 'okcupid', 'squaredcircle', 'makeupaddiction', 'trees', 'reactiongifs', 'india',
		'askreddit', 'screenshots', 'askscience', 'sex'
	]
	
	parse = argparse.ArgumentParser(description = 'LinkFixerBot')
	parse.add_argument('-l', '--login', action = 'store_true', help = 'Login to a different account than config account')
	args = parse.parse_args()
	
	print('\nLFB // version ' + version)
	print('------------------')
	
	if not os.path.isfile(config_name):
		
		config.write(default, config_name)
		print('> Created config.json. Please edit the values in the config before continuing.')
		sys.exit()
		
	conf = config.load(config_name)
	
	if conf['limit'] == '':
		
		print('> The limit in the config is not set! Please set it to a proper number.')
		sys.exit()
		
	elif conf['limit'] > '500':
		
		print('> The limit in the config is over 500! Please make it a lower number.')
		sys.exit()
		
	if args.login:
		
		user = raw_input('> Reddit username: ')
		passwd = getpass.getpass("> %s's password: " % user)
		
		print
		
	else:
		
		user = conf['credentials']['username']
		passwd = conf['credentials']['password']
		
	agent = (
		'/u/' + user + ' running LinkFixerBot, version ' + version
	)
	
	r = praw.Reddit(user_agent = agent)
	reddit.login(user, passwd, r)
	
	loop(r, conf, banned)
	
def loop(reddit, config, banned):
	
	cache = []
	
	print('\n> Booting up LFB. You will be notified when LFB detects a broken link.')
	print('> To stop the bot, press Ctrl + C.')
	
	try:
		
		while True:
			
			comments = reddit.get_comments('all', limit = config['limit'])
			
			for comment in comments:
				
				cond, links = check(comment)
				
				if cond and comment.subreddit.display_name.lower() not in banned and comment.id not in cache:
					
					print('\n> Valid comment found in the sub /r/%s!' % comment.subreddit.display_name)
					cache = post(comment, links, cache)
					
			time.sleep(15)
			
	except KeyboardInterrupt:
		
		print('\n> Stopped LFB. Thank you for running this bot!')
		
def check(comment):
	
	body = comment.body
	links = set(re.findall(sub_regex, body))
	cond = False
	
	if links:
		
		cond = True
		
	return cond, links
	
def post(comment, links, cache):
	
	denied_links = ''
	fixed = ''
	
	for c in links:
	
		text = '/' + c[1:] + ' '
		
		if c[1:].lower() == 'r/' + comment.subreddit.display_name.lower():
		
			denied_links += text
		
		else:
			
			fixed += text
			
	if fixed == '':
		
		print('> All broken links are the same as the sub!')
		
	else:
		
		reply = (
			fixed + '\n\n'
			'*****\n'
			'^This ^is ^an [^automated ^bot](http://github.com/WinneonSword/LFB)^. ^For ^reporting ^**problems**, ^contact ^/u/WinneonSword.'
		)
		
		try:
			
			comment.reply(reply)
			cache.append(comment.id)
			
			print('> Comment posted! Fixed links: %s' % fixed)
			
			if not denied_links == '':
				
				print('> Denied links: %s' % denied_links)
				
		except:
			
			print('> Failed to post comment.')
			
	return cache
	
bootup()