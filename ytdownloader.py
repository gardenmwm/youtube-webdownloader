from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
import queue
import threading
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ytdownloader.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(100), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/addtoqueue', methods=['POST'])
def addtoqueue():
    url = request.form['url']
    destination = request.form['destination']
    status = 'Pending'
    title = 'Unknown'
    channel = 'Unknown'
    video = Video(url=url, status=status, destination=destination, title=title, channel=channel)
    db.session.add(video)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/addtoqueueredirect', methods=['POST'])
def addtoqueueredirect():
    url = request.form['url']
    destination = request.form['destination']
    status = 'Pending'
    title = 'Unknown'
    channel = 'Unknown'
    video = Video(url=url, status=status, destination=destination, title=title, channel=title)
    db.session.add(video)
    db.session.commit()
    return redirect(url)



def download_thread(name):
    while True:
        video = Video.query.filter_by(status='Pending').first()
        if video is not None:
            print("Downloading video")
            video.status = 'Downloading'
            db.session.commit()
            output=subprocess.check_output(['yt-dlp', '-o', os.path.join(video.destination, '%(channel)s/%(title)s.%(ext)s'), '--remux-video', 'mp4', video.url])
            print(output)
            video.status = 'Downloaded'
            db.session.commit()
        else:
            time.sleep(10)


x=threading.Thread(target=download_thread, args=(1,))
x.start()