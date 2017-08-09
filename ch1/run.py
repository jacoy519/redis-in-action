import redis
import time


ONE_WEEK_IN_SECONDS=7 * 86400
VOTE_SCORE = 432
def article_vote(conn, user, article):
	cutoff = time.time() - ONE_WEEK_IN_SECONDS
	if conn.zscore('time:', article) < cutoff:
		return
	article_id = article.partition(':')[-1]
	if conn.sadd('voted:' + article_id, user):
		conn.zincrby('score:', article, VOTE_SCORE)
		conn.hincrby(article, 'votes',1)


def post_article(conn, user, title, link):
	article_id = str(conn.incr('article:'))
	voted = 'voted:' + article_id
	conn.sadd(voted, user)
	conn.expire(voted, ONE_WEEK_IN_SECONDS)
	now = time.time()
	article = 'article:' + article_id
	conn.hmset(article, {
		'title' : title,
		'link' : link,
		'poster' : user,
		'time' : now,
		'votes' : 1			
	})
	conn.zadd('score:', article, now+VOTE_SCORE)
	conn.zadd('time:', article, now)

ARTICLES_PER_PAGE = 25
def get_article(conn, page, order='score:'):
	start = (page-1) * ARTICLES_PER_PAGE
	end = start + ARTICLES_PER_PAGE -1 
	ids = conn.zrevrange(order, start, end)
	articles = []
	for id in ids:
		article_data = conn.hgetall(id)
		article_data['id'] = id
		articles.append(article_data)
	return articles

def add_remove_groups(conn, article_id, to_add=[], to_remove=[]):
	article = 'article:' + article_id
	for group in to_add:
		conn.sadd('group:' + group, article)
	for group in to_remove:
		conn.srem('group:' + group, article)
	
conn = redis.Redis()
for i in range(0,50):
	post_article(conn, 'user:123456','test_title','test_link')
for i in range(0,50):
	article_vote(conn, 'user:' + str(i),'article:' + str(i))
articles = get_article(conn, 1)
for article in articles:
	print 'get ' + article['id']

