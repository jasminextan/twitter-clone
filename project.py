'''
This is a "hello world" flask webpage.
During the last 2 weeks of class,
we will be modifying this file to demonstrate all of flask's capabilities.
This file will also serve as "starter code" for your Project 5 Twitter webpage.

NOTE:
the module flask is not built-in to python,
so you must run pip install in order to get it.
After doing do, this file should "just work".
'''
import sqlite3
from flask import Flask, render_template, request, make_response, redirect, url_for
from datetime import datetime
import bleach
import markdown_compiler
from flask_babel import Babel, gettext 
app = Flask(__name__) #creates an app for us
app.config['BABEL_DEFAULT_LOCALE'] ='es'
babel = Babel(app)

con = sqlite3con = sqlite3.connect('twitter_clone.db')
cur = con.cursor()
import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
DATABASE = 'twitter_clone.db'
args = parser.parse_args()

from werkzeug.security import generate_password_hash, check_password_hash

def print_debug_info():
    # Get method
    print('request.args.get("username")=', request.args.get('username'))
    print('request.args.get("password")=', request.args.get('password'))
    # Post Method 
    print('request.form.get("username")=', request.form.get('username'))
    print('request.form.get("password")=', request.form.get('password'))
    # Cookies
    print('request.cookies.get("username")=', request.cookies.get('username'))
    print('request.cookies.get("password")=', request.cookies.get('password'))

@babel.localeselector
def get_locale():
    
    request.accept_languages.best_match(['es', 'el'])

# class id(DATABASE): 
#     # ...

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

@app.route('/') #index page
def root():

    # connect to the database
    con = sqlite3.connect(DATABASE)
    # construct messages,
    # which is a list of dictionaries,
    # where each dictionary contains the information about a message
    messages = []

    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username,password)
    print('good_credentials=', good_credentials)

    sql = """
    SELECT sender_id,message,created_at
    FROM messages
    ORDER BY created_at DESC; 
    """
    cur_messages = con.cursor()
    cur_messages.execute(sql)
    for row_messages in cur_messages.fetchall():

        # convert sender_id into a username
        sql="""
        SELECT username,age
        FROM users
        WHERE id=?;
        """
        cur_users = con.cursor()
        cur_users.execute(sql, [row_messages[0]])
        for row_users in cur_users.fetchall():

            # build the message dictionary
            messages.append({
                'message': row_messages[1],
                'username': row_users[0],
                'created_at': row_messages[2],
                'profpic': 'https://robohash.org/' + row_users[0],
                'age':row_users[1],
                })
    # render the jinja2 template and pass the result to firefox
    return render_template('root.html', messages=messages, logged_in=good_credentials)

def are_credentials_good(username,password):
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    username=username
    sql = """
    SELECT password FROM users where username= ?;
    """
    cur.execute(sql,[username])
    for row in cur.fetchall():
        if password == row[0]:
            return True
        else:
            return False 
        
    # if username=='haxor' and password=='1337':
    #     return True
    # else:
    #     return False

def markdown(comment):
    if comment is not None:
        comment_list=comment.split(' ')
        if any('https://' in word for word in comment_list) or any('http://' in word for word in comment_list):
            print(comment_list)
            comment_link = bleach.linkify(comment)
            comment_converted=markdown_compiler.compile_lines('\n'+comment_link+'\n')
            comment_converted_clean=bleach.clean(comment_converted, tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 
            'code', 'em', 'i', 'li', 'ol', 'strong', 'ul', 'p'], attributes=['style', 'href', 'rel'])
            return comment_converted_clean
        else:
            comment_converted=markdown_compiler.compile_lines('\n'+comment+'\n')
            comment_converted_clean=bleach.clean(comment_converted, tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 
            'code', 'em', 'i', 'li', 'ol', 'strong', 'ul', 'p'], attributes=['style', 'href'])
            return comment_converted_clean
    else:
        return comment

@app.route('/login', methods=['GET', 'POST'])
def login():
    print_debug_info()
    username=request.form.get('username')
    password=request.form.get('password')
    print("username=",username)
    print("password=",password)

    good_credentials=are_credentials_good(username,password)
    print('good_credentials=',good_credentials)

    if username is None:
        return render_template('login.html', bad_credentials=False)
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:

            #If we get here then we are logged in, they typed the correct information
            
            #return 'login successful'
            response = make_response(redirect(url_for('root')))
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response

@app.route('/logout')
def logout():
    res = make_response(render_template('logout.html'))
    res.set_cookie('username', '', expires=0)
    res.set_cookie('password', '', expires=0)
    return res

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    username=request.form.get('username')
    password=request.form.get('password')
    password1=request.form.get('password1')
    age=request.form.get('age')
    print(username, password, password1, age)
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    sql = """
    INSERT INTO users (username, password, age) VALUES (?, ?, ?);
    """
    if username:
        if password==password1:
            try:
                cur.execute(sql, [username, password, age])
                con.commit()
                response = make_response(redirect(url_for('root')))
                response.set_cookie('username', username)
                response.set_cookie('password', password)
                return response
            except:
                return render_template('create_user.html', usercreated= False, error= True )
        else:
            return render_template('create_user.html', usercreated= False, typo=True)
    else:
        return render_template('create_user.html', usercreated= False, error= False)

  
@app.route('/create_message', methods=['get', 'post'])
def create_message():
    if(request.cookies.get('username') and request.cookies.get('password')):
        if request.form.get('newMessage'):
            con = sqlite3.connect(DATABASE)
            cur = con.cursor()
            username = request.cookies.get('username')
            user_id = ''
            if username != None:
                sql = '''
                SELECT id FROM users WHERE username=?;
                '''
                cur.execute(sql, [username])
                for row in cur.fetchall():
                    user_id += str(row[0])
            time = datetime.now()
            time = time.strftime("%Y-%m-%d %H:%M:%S")
            cur.execute('''
                INSERT INTO messages (sender_id, message) values (?, ?);
            ''', (user_id, markdown(request.form.get('newMessage'))))
            con.commit()
            return make_response(render_template('create_message.html', created=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else:
            return make_response(render_template('create_message.html', created=False, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return login()




@app.route('/search_message', methods=['POST', 'GET'])
def search_message():
    if request.form.get('search'):
        con = sqlite3.connect(DATABASE) 
        cur = con.cursor()
        cur.execute('''
            SELECT sender_id, message, created_at, id from messages;
        ''')
        rows = cur.fetchall()
        messages = []
        for row in rows:
            if request.form.get('search') in row[1]:
                messages.append({'username': row[0], 'text': row[1], 'created_at':row[2], 'id':row[3]})
        messages.reverse()
        return render_template('search_message.html', messages=messages, username=request.cookies.get('username'), password=request.cookies.get('password'))
    else:
        return render_template('search_message.html', default=True, username=request.cookies.get('username'), password=request.cookies.get('password'))

@app.route('/change_password/<username>', methods=['post', 'get'])
def change_password(username):
    if request.form.get('oldPassword'):
        if request.cookies.get('username') == username:
            con = sqlite3.connect(DATABASE) 
            cur = con.cursor()
            cur.execute('''
                SELECT password from users where username=?;
            ''', (username,))
            rows = cur.fetchall()
            oldPassword = rows[0][0]
            
            if request.form.get('oldPassword') == oldPassword:
                if request.form.get('password1') == request.form.get('password2'):
                    cur.execute('''
                        UPDATE users
                        SET password = ?
                        WHERE username = ?
                    ''', (request.form.get('password1'), request.cookies.get('username')))
                    con.commit()
                    return make_response(render_template('change_password.html', allGood=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
                else: 
                    return make_response(render_template('change_password.html', repeatPass=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
            else: 
                return make_response(render_template('change_password.html', wrongPass=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else: 
            return make_response(render_template('change_password.html', not_your_username=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else: return make_response(render_template('change_password.html', username=request.cookies.get('username'), password=request.cookies.get('password')))

@app.route('/user')
def user():
    if(request.cookies.get('username') and request.cookies.get('password')):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute('''
            SELECT message, created_at, id from messages where sender_id=?;
        ''', (request.cookies.get('username'),))
        rows = cur.fetchall()
        messages = []
        for row in rows:
            messages.append({'text': row[0], 'created_at': row[1], 'id':row[2]})
        messages.reverse()
        return make_response(render_template('user.html', messages=messages, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else: 
        return login()


@app.route('/delete_account/<username>')
def delete_account(username):
    if request.cookies.get('username') == username:
        con = sqlite3.connect(args.db_file) 
        cur = con.cursor()
        cur.execute('''
            DELETE from users where username=?;
        ''', (username,))
        con.commit()
        res = make_response(render_template('delete_account.html'))
        res.set_cookie('username', '', expires=0)
        res.set_cookie('password', '', expires=0)
        return make_response(res)
    else:
        return make_response(render_template('delete_account.html', not_your_username=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
'''@app.route('/static')s
def create_static():
    return render_template('static')'''

@app.route('/edit_message/<id>', methods=['POST', 'GET'])
def edit_message(id):
    if request.form.get('newMessage'):
        con = sqlite3.connect(args.db_file) 
        cur = con.cursor()
        cur.execute('''
            SELECT sender_id, message from messages where id=?;
        ''', (id,))
        rows = cur.fetchall()
        if rows[0][0] == request.cookies.get('username'):
            cur.execute('''
                UPDATE messages
                SET message = ?
                WHERE id = ?
            ''', (request.form.get('newMessage'),id))
            con.commit()
            return make_response(render_template('edit_message.html',allGood=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else:
            return make_response(render_template('edit_message.html',not_your=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return make_response(render_template('edit_message.html',default=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))

app.run()


@app.route('/edit_message/<id>', methods=['POST', 'GET'])
def edit_message(id):
    if request.form.get('newMessage'):
        con = sqlite3.connect(DATABASE) 
        cur = con.cursor()
        cur.execute('''
            SELECT sender_id, message from messages where id=?;
        ''', (id,))
        rows = cur.fetchall()
        if rows[0][0] == request.cookies.get('username'):
            cur.execute('''
                UPDATE messages
                SET message = ?
                WHERE id = ?
            ''', (request.form.get('newMessage'),id))
            con.commit()
            return make_response(render_template('edit_message.html',allGood=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else:
            return make_response(render_template('edit_message.html',not_your=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return make_response(render_template('edit_message.html',default=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))

app.run()