import subprocess

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
scheduler = BackgroundScheduler()

def run_shell(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, check=True).stdout.decode()
    return result

@scheduler.scheduled_job('cron', hour=00, minute=00)
def start_torrents():
	run_shell('transmission-remote -t all --start')

@scheduler.scheduled_job('cron', hour=5, minute=59)
def stop_torrents():
	run_shell('transmission-remote -t all --stop')

@app.route('/')
def index():
    active_torrents = run_shell('transmission-remote --list').split('\n')
    header, torrents = active_torrents[0], active_torrents[1:]
    return render_template('index.html', header=header, torrents=torrents)

@app.route('/add', methods=['POST'])
def add_torrent():
    url = request.form['url']
    run_shell(f'transmission-remote --add --start-paused "{url}"')
    return redirect(url_for('index'))

if __name__ == '__main__':
	scheduler.start()
	app.run(host='0.0.0.0')
