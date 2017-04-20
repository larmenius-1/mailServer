#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import logging, logging.config
import smtpd
import asyncore
import sqlite3
import os


# check if database exists, create it otherwise
def checkDatabase() :
	database_name = config["database"]
	print("Database : {0}".format(database_name))
	if not os.path.isfile(database_name):
		logger.warning("Database {} does not exist -> Creation".format(database_name))
	else :
		logger.info("Checking database {}".format(database_name))
	db = sqlite3.connect(database_name)
	cursor = db.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, login TEXT, password TEXT)")
	cursor.execute("CREATE TABLE IF NOT EXISTS mail (id INTEGER PRIMARY KEY, user INTEGER, body TEXT)")
	db.close

#import sqlite3
#conn = sqlite3.connect('example.db')
#c = conn.cursor()
# Create table
#c.execute('''CREATE TABLE stocks(date text, trans text, symbol text, qty real, price real)''')

# Insert a row of data
#c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

# Save (commit) the changes
#conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
#conn.close()

#t = ('RHAT',)
#c.execute('SELECT * FROM stocks WHERE symbol=?', t)
#print c.fetchone()
#for row in c.execute('SELECT * FROM stocks ORDER BY price'):
#        print row

####

class CustomSMTPServer(smtpd.SMTPServer) :
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        logger.debug("Receiving message from: {0}".format(peer))
        logger.debug("Message addressed from: {} to {}".format(mailfrom,rcpttos))
        logger.debug("Message length : {} \n{}\n".format(len(data),data))
        return

####

# load configuration, with default values when not found
def loadConfig() :
	logger.info("Lecture de la configuration")

	config=configparser.ConfigParser()
	config.read("mail.ini")

	try :
		section=config["mail"]
	except KeyError as exception :
		logger.critical("Paramètres inconnus -> valeurs par défaut")
		section = {}

	cfg={}
	cfg["server"]=section.get("server","localhost")
	cfg["smtp.port"]=int(section.get("smtp.port","10025"))
	cfg["pop.port"]=int(section.get("pop.port","10119"))
	cfg["database"]=section.get("database","localhost")
	return cfg


# main

if __name__ == "__main__" :
	logging.config.fileConfig("mail.ini")
	logger=logging.getLogger("root")

	config=loadConfig()
	logger.debug("{0}".format(config))
	checkDatabase()
	server = CustomSMTPServer((config["server"], config["smtp.port"]), None)
	#print("{0}".format(server));

	logger.info("--- Start on {0}:{1} ---".format(config["server"], config["smtp.port"]))
	#asyncore.loop()
	logger.info("--- Stop ---")

