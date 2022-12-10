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
app = Flask(__name__) #creates an app for us
con = sqlite3con = sqlite3.connect('twitter_clone.db')
cur = con.cursor()
# args.db_file = 'twitter_clone.db'
import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
args = parser.parse_args()

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


@app.route('/') #index page
def root():
    # connect to the database
    con = sqlite3.connect(args.db_file)
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
            pass

        # build the message dictionary
        messages.append({
            'message': row_messages[1],
            'username': row_users[0],
            'created_at': row_messages[2],
            
            'age':row_users[1],
            })
    # render the jinja2 template and pass the result to firefox
    return render_template('root.html', messages=messages, logged_in=good_credentials)

def are_credentials_good(username,password):
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
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
    response = make_response(render_template('logout.html'))
    response.delete_cookie('username')
    response.delete_cookie('password')
    return response

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
                return render_template('create_user.html', usercreated=True)
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
            con = sqlite3.connect(args.db_file)
            cur = con.cursor()
            cur.execute('''
                INSERT INTO messages (sender_id, message) values (?, ?);
            ''', (request.cookies.get('username'), request.form.get('newMessage')))
            con.commit()
            return make_response(render_template('create_message.html', created=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else:
            return make_response(render_template('create_message.html', created=False, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return login()


@app.route('/search_message', methods=['POST', 'GET'])
def search_message():
    if request.form.get('search'):
        con = sqlite3.connect(args.db_file) 
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

@app.route('/delete_account/<username>')
def delete_account(username):
    if request.cookies.get('username') == username:
        con = sqlite3.connect(args.db_file) 
        cur = con.cursor()
        cur.execute('''
            DELETE from users where username=?;
        ''', (username,))
        con.commit()
        return make_response(render_template('delete_account.html', not_your_username=False, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return make_response(render_template('delete_account.html', not_your_username=True, username=request.cookies.get('username'), password=request.cookies.get('password')))


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
'''@app.route('/static')s
def create_static():
    return render_template('static')'''

app.run()