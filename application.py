from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "sjfgiefyhube"
DB_URL = 'mysql://{user}:{pw}@{url}/{db}'.format(user='root', pw='root', url='localhost',
                                                 db='students')

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'scholarships'
    scholarships = db.Column(db.String(200), unique=True, nullable=False, primary_key=True)
    faculty = db.Column(db.String(100), unique=False, nullable=False)
    link = db.Column(db.String(1000), unique=False, nullable=False)
    state = db.Column(db.String(100), unique=False, nullable=False)
    total_value = db.Column(db.Integer, unique=False, nullable=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit():
    scholar = []
    sum_total = 0
    a_list = User.query.filter_by(faculty=request.form["faculty"],
                                        state=request.form["Equity"] and request.form["Merit"] and request.form[
                                            "Leadership"] and
                                              request.form["Placement"]).all()
    for item in a_list:
        scholar.append({"scholarship":  item.scholarships, "money": item.total_value})
        sum_total += int(item.total_value)
    return render_template("scholarship.html", lists=scholar, sum=sum_total)




app.run("0.0.0.0", "8080")
