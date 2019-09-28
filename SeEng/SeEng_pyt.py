from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)

@app.route('/Admin')
def admin():
	return render_template('Search_Eng_Admin.html')

@app.route('/Home')
def home():
	return render_template('Search_Eng_TBR.html')

@app.route('/Use')
def user():
	return render_template('Search_Eng_User.html')

	
if __name__ == '__main__':
	app.run(debug = True)