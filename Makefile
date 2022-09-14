setup:
	pip install --upgrade pip
	pip install -r requirements.txt
	sqlite3 messages.db < messages.sql

db:
	sqlite3 messages.db < messages.sql
start:
	python3 app.py