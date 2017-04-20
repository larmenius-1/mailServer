#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import logging, logging.config
import smtpd
import asyncore
import sqlite3
import os
import sys
import argparse


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


# parse command line args
def commandLine() :
	parser=argparse.ArgumentParser()
	group=parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-add", nargs=2, metavar=("user@domain.xxx", "password"), help="Crée un utilisateur")
	group.add_argument("-delete", nargs=1, metavar="USER", help="Supprime un utilisateur")
	group.add_argument("-list", action="store_true", help="Liste les utilisateurs")
	group.add_argument("-dump", nargs=1, metavar="USER", help="Liste les messages d'un utilisateur")
	group.add_argument("-start", action="store_true", help="Démarre le serveur")

	return parser.parse_args()
#	print(opts)
#	print(opts.add)
#	print(opts.delete)
#	print(opts.list)
#	print(opts.dump)
#	print(opts.start)
	

"""
import argparse

# Use nargs to specify how many arguments an option should take.
ap = argparse.ArgumentParser()
ap.add_argument('-a', nargs=2)
ap.add_argument('-b', nargs=3)
ap.add_argument('-c', nargs=1)

# An illustration of how access the arguments.
opts = ap.parse_args('-a A1 A2 -b B1 B2 B3 -c C1'.split())

print(opts)
print(opts.a)
print(opts.b)
print(opts.c)

# To require that at least one option be supplied (-a, -b, or -c)
# you have to write your own logic. For example:
opts = ap.parse_args([])
if not any([opts.a, opts.b, opts.c]):
    ap.print_usage()
    quit()

#
# Use nargs to specify how many arguments an option should take.
ap = argparse.ArgumentParser()
group = ap.add_mutually_exclusive_group(required=True)
group.add_argument('-a', nargs=2)
group.add_argument('-b', nargs=3)
group.add_argument('-c', nargs=1)


# Grab the opts from argv
opts = ap.parse_args()

# This line will not be reached if none of a/b/c are specified.
# Usage/help will be printed instead.

print(opts)
print(opts.a)
print(opts.b)
print(opts.c)
"""

# execute the line parameters commands
def executeCommand(options) :
	# on rend la main pour demarrer le serveur
	if options.start :
		return

	exit(1)


# main

if __name__ == "__main__" :
	logging.config.fileConfig("mail.ini")
	logger=logging.getLogger("root")

	config=loadConfig()
	logger.debug("{0}".format(config))

	checkDatabase()

	options=commandLine()
	executeCommand(options)

	if options.start :
		#server = CustomSMTPServer((config["server"], config["smtp.port"]), None)
		#print(server);
		print("starting")

		logger.info("--- Start on {0}:{1} ---".format(config["server"], config["smtp.port"]))
		#asyncore.loop()
		logger.info("--- Stop ---")

