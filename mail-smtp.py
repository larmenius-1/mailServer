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
import signal



####

class CustomSMTPServer(smtpd.SMTPServer) :

	def process_message(self, peer, mailfrom, rcpttos, data):
		length = len(data)
		logger.debug("Receiving message from: {0}".format(peer))
		logger.debug("Message addressed from: {0} to {1}".format(mailfrom,rcpttos))
		logger.debug("Message length : {0} \n{1}\n".format(length,data))

		print("Message addressed from: {0} to {1}".format(mailfrom,rcpttos))
		print("Message length : {0} \n{1}".format(length,data))
		print("---")

		db = sqlite3.connect(config["database"])
		cursor = db.cursor()
		# on duplique le message pour chaque destinataire
		for email in rcpttos :
			cursor.execute("SELECT email FROM user WHERE email = ?", (email,))
			user = cursor.fetchone()
			if None == user :
				logger.warning("Utilisateur {0} inconnu !".format(email))
				continue
			cursor.execute("INSERT INTO mail(mail_address, length, mail_body) VALUES(?, ?, ?)", (email, length, data))

		db.commit()
		db.close()
		return

####

# load configuration, with default values when not found
def loadConfig() :
	logger.info("Lecture de la configuration.")

	config=configparser.ConfigParser()
	config.read("mail.ini")

	try :
		section=config["mail"]
	except KeyError as exception :
		logger.critical("Paramètres inconnus -> valeurs par défaut.")
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
	group.add_argument("-delete", nargs=1, metavar="user@domain.xxx", help="Supprime un utilisateur")
	group.add_argument("-list", action="store_true", help="Liste les utilisateurs")
#	group.add_argument("-dump", nargs=1, metavar="user@domain.xxx", help="Liste les messages d'un utilisateur")
	group.add_argument("-clear", nargs=1, metavar="user@domain.xxx", help="Supprime les messages d'un utilisateur")
	group.add_argument("-start", action="store_true", help="Démarre le serveur")
	# only for help
	group.add_argument("-stop", action="store_true", help="Arrête le serveur")

	return parser.parse_args()
	

# execute the line parameters commands
def executeCommand(options) :
	# on rend la main pour demarrer le serveur
	if options.start :
		return

	database_name = config["database"]

	# ajout d'un utilisateur
	if options.add :
		email, password = options.add
		db = sqlite3.connect(database_name)
		cursor = db.cursor()
		cursor.execute("SELECT email FROM user WHERE email = ?", (email,))
		user = cursor.fetchone()
		if user :
			message = "Utilisateur {0} déjà défini !".format(email)
			print("{0}\n".format(message))
			logger.error(message)
			exit(1)
		else :
			cursor.execute("INSERT INTO user(email,password) VALUES(?,?)", (email, password))
			message = "Utilisateur {0} créé.".format(email)
			print("{0}\n".format(message))
			logger.info(message)
			db.commit()
		db.close()
		exit(0)

	# liste des utilisateurs
	if options.list :
		db = sqlite3.connect(database_name)
		cursor = db.cursor()
		cursor.execute("SELECT email FROM user ORDER BY email")
		data = cursor.fetchall()
		if 0 == len(data) :
			print("Aucun utilisateur défini\n")
		else :
			print("{0:40} : {1}".format("email","Msg"))
			print("{} : {}".format("-" * 40, "-" * 3))
			for user in data :
				email = user[0]
				cursor.execute("SELECT COUNT(id) FROM mail where mail_address = ?", (email,))
				nbMessages = cursor.fetchone()[0]
				print("{0:40} : {1:>3}".format(email, nbMessages))
			print()
		db.close()
		exit(0)
		
	# suppression d'un utilisateur
	if options.delete :
		email = options.delete[0]
		db = sqlite3.connect(database_name)
		cursor = db.cursor()
		cursor.execute("SELECT email FROM user WHERE email = ?", (email,))
		user = cursor.fetchone()
		if None == user :
			print("Utilisateur {0} inconnu !\n".format(email))
		else :
			nbMessages = cursor.execute("DELETE FROM mail WHERE mail_address = ?", (email,)).rowcount
			message = "{0} messages supprimés".format(nbMessages)
			logger.info(message)
			print(message)
			cursor.execute("DELETE FROM user WHERE email = ?", (email,))
			db.commit()
			message = "Utilisateur {0} supprimé".format(email)
			logger.info(message)
			print(message)
		db.close()
		exit(0)

	# suppression des messages d'un utilisateur
	if options.clear :
		email = options.clear[0]
		db = sqlite3.connect(database_name)
		cursor = db.cursor()
		cursor.execute("SELECT email FROM user WHERE email = ?", (email,))
		user = cursor.fetchone()
		if None == user :
			print("Utilisateur {0} inconnu !\n".format(email))
		else :
			nbMessages = cursor.execute("DELETE FROM mail WHERE mail_address = ?", (email,)).rowcount
			db.commit()
			message = "{0} messages supprimés pour {1}".format(nbMessages,email)
			logger.info(message)
			print(message)
		db.close()
		exit(0)

	# on a rien traité, on sort
	exit(1)


# check existence of user/email in database
def checkUser(email) :
	if None == email :
		logger.error("Utilisateur non défini.")
		return False

	db = sqlite3.connect(config["database"])
	cursor = db.cursor()
	cursor.execute("SELECT email FROM user WHERE email = ?", (email,))
	user = cursor.fetchone()
	db.close()
	return None != user 


# check if database exists, create it otherwise
def checkDatabase() :
	database_name = config["database"]
	if not os.path.isfile(database_name):
		logger.warning("Database {0} does not exist -> Creation.".format(database_name))
	else :
		logger.info("Checking database {0}.".format(database_name))
	db = sqlite3.connect(database_name)
	cursor = db.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
	cursor.execute("CREATE TABLE IF NOT EXISTS mail (id INTEGER PRIMARY KEY, mail_address TEXT, length INTEGER, mail_body TEXT)")
	db.close()


def exitGracefully(signum, frame) :
	# restore the original signal handler as otherwise evil things will happen 
	# and our signal handler is not re-entrant
	signal.signal(signal.SIGTERM, original_sigterm)
	signal.signal(signal.SIGINT, original_sigint)
	smtpServer.close()
#	popServer.close()

####

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
		# store the original signal handlers
		original_sigterm = signal.getsignal(signal.SIGTERM)
		signal.signal(signal.SIGTERM, exitGracefully)
		original_sigint = signal.getsignal(signal.SIGINT)
		signal.signal(signal.SIGINT, exitGracefully)

		smtpServer = CustomSMTPServer((config["server"], config["smtp.port"]), None)
		#print(server);
		print("starting")

		logger.info("--- Start on {0}:{1} ---".format(config["server"], config["smtp.port"]))
		asyncore.loop()
		logger.info("--- Stop ---")

