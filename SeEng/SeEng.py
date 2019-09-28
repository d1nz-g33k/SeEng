import os
import sqlite3 as sql
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup, jsonify
#import flask.ext.wtf
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from werkzeug.utils import secure_filename



import datetime as dt
from datetime import timedelta

g_usr=""
g_url=""
g_fname=""
g_key=""

UPLOAD_FOLDER = './SeEng/templates/Uploads/'
ALLOWED_EXTENSIONS = set(['html'])

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , SeEng.py
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

f=1

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'SeEng.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    db = sql.connect(app.config['DATABASE'])
    #db.row_factory = sql.Row
#    db.execute('drop table USER')
#    db.execute('drop table UPLOAD')
#    db.execute('drop table HISTORY')    
#    db.execute('drop table RANK')
    db.execute('CREATE TABLE IF NOT EXISTS UPLOAD(URL VARCHAR PRIMARY KEY NOT NULL, fname VARCHAR NOT NULL, key VARCHAR NOT NULL, subK VARCHAR NOT NULL, key2 VARCHAR, path VARCHAR NOT NULL, desc VARCHAR NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS USER(Name VARCHAR NOT NULL, uname VARCHAR PRIMARY KEY NOT NULL, Eid VARCHAR NOT NULL, pswd VARCHAR NOT NULL, dob DATE NOT NULL, adrss VARCHAR NOT NULL, no INT NOT NULL, gender VARCHAR NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS HISTORY(uname VARCHAR NOT NULL, URL VARCHAR NOT NULL, fname VARCHAR NOT NULL, key VARCHAR NOT NULL, time VARCHAR NOT NULL, status VARCHAR NOT NULL, FOREIGN KEY(uname) REFERENCES USER(uname), FOREIGN KEY(URL) REFERENCES UPLOAD(URL), FOREIGN KEY(fname) REFERENCES UPLOAD(fname), FOREIGN KEY(key) REFERENCES UPLOAD(key))')
    db.execute('CREATE TABLE IF NOT EXISTS RANK(Rank INT NOT NULL, fname VARCHAR NOT NULL)')
    return db

def close_db(db):
    db.commit()
    db.close()

@app.route('/Home', methods=['GET', 'POST'])
def home():
    global g_usr
    db=connect_db()
    c=db.cursor()
    c.execute('SELECT Count() FROM USER')
    R = c.fetchone()[0]

    error = None
    if request.method == 'POST':
        g_usr=request.form.get('nm', None)
        if request.form.get('nm', None) != (app.config['USERNAME']):
            E='Invalid username'
            c.execute('SELECT Count() FROM USER')
            N=c.fetchone()
            c.execute('SELECT uname FROM USER')
            r=c.fetchall()
            for i in range(0,N[0]):
                m=str(r[i])
                q=request.form.get('nm', None)
                p="('"+q+"',)"
                if p == m:
                    M=[m]
                    c.execute('SELECT pswd FROM USER WHERE uname=?', (q,))
                    pswd=c.fetchone()[0]
                    if(request.form.get('pwd', None) == pswd):
                        session['User'] = True
                        E='You are logged in'
                        flash(E)
                        return redirect(url_for('user'))
                    else:
                        E='Invalid password'
                        flash(E)    
        #elif request.form.get('nm', None) == 
        
        elif request.form.get('pwd', None) != app.config['PASSWORD']:
            F='Invalid password'
            flash(F)
        
        else:
            session['Admin'] = True
            flash('You are logged in')
            return redirect(url_for('admin'))
            
            #db = get_db()
    #c=db.execute('')
    #r=c.fetchall()
    close_db(db)
    return render_template('Search_Eng_TBR.html', error=error)

@app.route('/home', methods=['GET', 'POST'])
def logout():
    session['User'] = False
    session['Admin'] = False
    return home()

class upload(Form):
    """
    Rform
    """
    url = TextField('Name:', validators=[validators.required()])
    fname = TextField('FileName:', validators=[validators.required()])
    fkey = TextField('File Key:', validators=[validators.required()])
    skey = TextField('Sub Key:', validators=[validators.required()])
    k2 = TextField('Secondary Key:', validators=[validators.required()])


class Rform(Form):
    """
    Rform
    """
    #url = TextField('url')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/Admin', methods=['GET', 'POST'])
def admin():
    form = upload(request.form)
    db=connect_db()
    c=db.cursor()
    if request.method == 'POST':

        url=request.form.get('url')
        fn=request.form.get('fn')
        key=request.form.get('K')
        skey=request.form.get('subK')
        key2=request.form.get('k2')
        #f=request.form.get('file')
        msg=request.form.get('msg')
        
        t = request.files.getlist('file[]')

        E=""

        if (len(t)==1 and url!="" and fn!="" and key!="" and skey!="" and key2!="" and msg!=""):
            flash('Hello ')
        else:
            flash('Error: All the form fields are required. and a single file is must')

        if(len(t)==1):
            if allowed_file(t[0].filename):
                filename= secure_filename(t[0].filename)
                fname=t[0].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                f=open(app.config['UPLOAD_FOLDER']+'/'+ filename, 'r+')
                content=f.read()
                f.seek(0, 0)
                f.write("""
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script type="text/javascript">
window.onbeforeunload=function(){
    $.getJSON('/_out', { });
}
</script>
                \n"""+content)
                f.close()
                f=open(app.config['UPLOAD_FOLDER']+'/'+ filename, 'a')
                f.write("""
<script type="text/javascript">
window.onunload=ty()
function ty(){
    $.getJSON('/_in', { });
}
</script>       \n""")
                f.close()
                path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                D=[url, fn, key, skey, key2, path, msg]
                c.execute('INSERT INTO UPLOAD VALUES( ?, ?, ?, ?, ?, ?, ?)', D)
            else:
                E=E+'\n Check the format, only HTML files are supported'
                flash(E)
    close_db(db)
    #File = open(file)

    #if open.filename == '':
    #    flash('No selected file')
    #    return redirect(request.url)
    #if open and allowed_file(open.filename):
    #    filename = secure_filename(open.filename)
    #    open.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #    return redirect(url_for('uploaded_file', filename=filename))

    if session['Admin'] == False:
        flash('Please login')
        return render_template('Search_Eng_TBR.html')
    else:
        return render_template('Search_Eng_Admin.html', form=form)

@app.route('/_out')
def out():
    try:
        global g_url, g_fname, g_key, g_usr
        t=dt.datetime.now().time()
        tim=str(t)
        db=connect_db()
        c=db.cursor()
        #uname, url, fname, key, time, status
        #val={g_usr, g_url, g_fname, g_key, t, "OUT"}
        #print(val)
        c.execute("INSERT into HISTORY VALUES( ?, ?, ?, ?, ?, ?)", (g_usr, g_url, g_fname, g_key, tim, "OUT",))
        #close_db(db)
        return render_template('Search_Eng_TBR.html')
    except Exception as e:
        return(str(e))

@app.route('/_in')
def i_n():
    try:
        global g_url, g_fname, g_key, g_usr
        t=dt.datetime.now().time()
        tim=str(t)
        db=connect_db()
        c=db.cursor()
        #uname, url, fname, key, time, status
        #val={g_usr, g_url, g_fname, g_key, t, "OUT"}
        #print(val)
        c.execute("INSERT into HISTORY VALUES( ?, ?, ?, ?, ?, ?)", (g_usr, g_url, g_fname, g_key, tim, "IN",))
        #close_db(db)
        return render_template('Search_Eng_TBR.html')
    except Exception as e:
        return(str(e))

@app.route('/')
def index():
    return render_template('l.html')

@app.route('/User', methods=['GET', 'POST'])
def user():
    if session['User'] == False:
        flash('Please login')
        return render_template('Search_Eng_TBR.html')
    else:
        s=request.form.get('search')
        db=connect_db()
        c=db.cursor()
        c.execute("SELECT fname FROM UPLOAD WHERE key=? OR subK=? OR key2=?", (s, s, s,))
        r=c.fetchall()
        c.execute("SELECT desc FROM UPLOAD WHERE key=? OR subK=? OR key2=?", (s, s, s,))
        t=c.fetchall()
        c.execute("SELECT URL FROM UPLOAD WHERE key=? OR subK=? OR key2=?", (s, s, s,))
        q=c.fetchall()
        c.execute("SELECT path FROM UPLOAD WHERE key=? OR subK=? OR key2=?", (s, s, s,))
        s=c.fetchall()
        if len(r)!=0:
            i=len(r)
            result=Markup("<br>")
            for x in range(0,i):
                d=str(r[x])
                u=str(t[x])
                v=str(s[x])
                w=str(q[x])
                data=d.split("'")
                datb=u.split("'")
                datc=v.split("'")
                datd=w.split("'")
                result=result+Markup("<a href=user_req/"+datd[1]+">"+data[1]+"<br>"+datb[1]+"</a><br><br>")
            return render_template('Search_Eng_User.html', result=result)
        else:
            result = Markup("<b>Sorry, no results found<b>")
            return render_template('Search_Eng_User.html', result=result, f=f)

@app.route('/user_req/<pg>', methods=['GET', 'POST'])
def req(pg):
    global g_url, g_fname, g_key
    db=connect_db()
    c=db.cursor()
    g_url=pg
    c.execute("SELECT fname FROM UPLOAD WHERE url=?", (pg,))
    y=c.fetchall()
    g_fname=str(y)
    c.execute("SELECT key FROM UPLOAD WHERE url=?", (pg,))
    i=c.fetchall()
    g_key=str(i)
    c.execute("SELECT path FROM UPLOAD WHERE url=?", (pg,))
    r=c.fetchall()
    z=str(r)
    z=z.split("templates")
    dat=z[1].split("'")
    return render_template(dat[0])

@app.route('/register', methods=['GET', 'POST'])
def reg():
    form = Rform(request.form)
    db=connect_db()
    c=db.cursor()

    if request.method=='POST':
        nm=request.form.get('nm')
        uname=request.form.get('uname')
        Eid=request.form.get('Eid')
        pswd=request.form.get('pswd')
        cpswd=request.form.get('cpswd')
        dob=request.form.get('dob')
        ad=request.form.get('ad')
        no=request.form.get('no')
        gender=request.form.get('gender')

        if (nm!="" and uname!="" and Eid!="" and pswd!="" and cpswd!="" and len(pswd)>=6 and cpswd==pswd and dob!="" and ad!="" and no!="" and gender!="--SELECT--"):
            L=[nm, uname, Eid, pswd, dob, ad, no, gender]
            c.execute('INSERT INTO USER VALUES( ?, ?, ?, ?, ?, ?, ?, ?)', L)
            flash("Hello")
        else:
            flash("Error: All the form fields are required. and a single file is must")
            flash("\nPassword must be atleast 6 characters")
        #print (dob)

    close_db(db)
            
            
    return render_template('register.html')


app.route('/Ime', methods=['GET', 'POST'])
def ime():
    try:
        t=dt.datetime.now().time()
        print(t)
        return render_template('Search_Eng_TBR.html')
    except Exception as e:
        return(str(e))

"""
def get_db():
    ""Opens a new database connection if there is none yet for the
    current application context.
    ""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    ""Closes the database again at the end of the request.""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    ""Initializes the database.""
    init_db()
    print('Initialized the database.')
    """