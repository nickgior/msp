
from flask import Flask, Response, request, make_response, render_template, redirect, url_for
from flaskext.mysql import MySQL
from random import randint


mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'msp'
app.config['MYSQL_DATABASE_PASSWORD'] = 'monkey2'
app.config['MYSQL_DATABASE_DB'] = 'msp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

SESSION_INTERVAL = 3 


def auth_user(username, password):
  cur = mysql.connect().cursor()
  cur.execute("SELECT id,ext_id,username,name FROM msp.user where username='%s' and password='%s'" % (username, password))
  if cur.rowcount == 1:
    rv = cur.fetchone()
    return rv[1]
  else:
    return False

def check_session():
  if 'msp_session' in request.cookies:
    cur = mysql.connect().cursor()
    cur.execute('''SELECT id, user_id FROM session WHERE id=%d and expires > NOW()''' % (int(request.cookies["msp_session"])) )
    if cur.rowcount == 1:
      rv = cur.fetchone()
      return rv[1]
    else:
      return False
  else:
    return False

def generate_session_id():
  session_id = 0
  x = 0
  if x == 0:
    cur = mysql.connect().cursor()
    cur.execute('''SELECT * FROM session ORDER BY id DESC LIMIT 0, 1''')
    if cur.rowcount == 1:
      session_id = cur.fetchone()[0] + 1
    else:
      session_id = 0
  elif x == 1:
    session_id = randint(0,10000)

  return session_id

def create_session(user_id):
  cnx = mysql.connect()
  cur = cnx.cursor()
  cur.execute('''DELETE FROM session WHERE user_id=%d''' % (user_id))
  cnx.commit()
  session_id = generate_session_id()
  cur.execute('''INSERT INTO session VALUES(%d,%d, DATE_ADD(NOW(), INTERVAL %d MINUTE))''' % (session_id, user_id, SESSION_INTERVAL) )
  cnx.commit()
  return session_id

def remove_session(session_id):
  cnx = mysql.connect()
  cur = cnx.cursor()
  cur.execute('''DELETE FROM session WHERE id=%d''' % (int(session_id)))
  cnx.commit()


@app.route('/hello')
def hello_world():
  hello_contents = []
  hello_contents.append("<html>")
  hello_contents.append("<title>Hello World</title>")
  hello_contents.append("<H2>Hello World</H2>")
  
  session = check_session()
  if not session:
    hello_contents.append("<p>No Session Found</p>")
  else:
    hello_contents.append("<p>Session Token: %s</p>" % (session))

  hello_contents.append("</html>")
  resp = Response( "\n".join(hello_contents) )
  resp.headers['X-XSS-Protection'] = '0'
  return resp

@app.route('/')
def site_index():
  resp = Response("Index")
  resp.headers['X-XSS-Protection'] = '0'
  return resp

@app.route('/product/<path:product_id>')
def product(product_id):
  resp = Response("Product: %s" % (product_id))
  resp.headers['X-XSS-Protection'] = '0'
  return resp

@app.route('/category')
def category():
  resp = Response("Category")
  resp.headers['X-XSS-Protection'] = '0'
  return resp

@app.route('/account')
def account():
  session = check_session()
  if not session:
    resp = make_response(redirect('/login?url=%s' % ("/account")))
    return resp
  else:
    resp = Response("Account")
    resp.headers['X-XSS-Protection'] = '0'
    return resp

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None

  if request.method == 'POST':
    u = request.form.get("url", default="/hello")
    user_id = auth_user(request.form['username'], request.form['password'])
    if user_id:
      session_id = create_session(user_id)
      resp = make_response(redirect( u ))
      resp.set_cookie('msp_session', str(session_id))
      return resp
    else:
      error = 'Invalid Credentials. Please try again.'
  else:
    u = request.args.get("url", default="/hello")
    # Check to see if they are already logged in
    if 'msp_session' in request.cookies:
      session = check_session()
      if session:
        error = "Cookie found: %s - <font color='green'>valid</font>" % (request.cookies["msp_session"])
      else: 
        error = "Cookie found: %s - <font color='red'>invalid</font>" % (request.cookies["msp_session"])

  resp = make_response( render_template('login.html', error=error, url=u) )
  resp.headers['X-XSS-Protection'] = '0'
  return resp

@app.route('/logout')
def logout():
  if 'msp_session' in request.cookies:
    remove_session( request.cookies["msp_session"] )

  resp = make_response(redirect('/hello'))
  resp.set_cookie('msp_session', '', expires=0)
  return resp


if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=5000)
