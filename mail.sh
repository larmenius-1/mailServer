#!/bin/sh

cd $HOME/python/mailServer

program=mail-smtp.py

if test $# = 0 ; then
	./$program -h
	exit 1
fi

# demarrage du serveur
if test "--start" = "-$1" ; then
	if test -f mail.pid ; then
		pid=`cat mail.pid`
		if test "0" != "0$pid" ; then
			if ps --no-header Op $pid | grep -q $program ; then
				echo "\033[0;31m$program already running !\033[00m"
				exit 1
			fi
		fi
	fi

	./$program -start &
	pid=$!
	echo $pid > mail.pid
	exit 0
fi

# arret du serveur
if test "--stop" = "-$1" ; then
	if test -f mail.pid ; then
		pid=`cat mail.pid`
		if test "0" != "0$pid" ; then
			if ps --no-header Op $pid | grep -q $program ; then
				echo Stopping $program
				kill -15 $pid
				rm mail.pid
				exit 0
			fi
		fi
		rm mail.pid
	fi

	echo "\033[0;31m$program not running !\033[00m"
	echo "Removing stalled PID"
	exit 0
fi

# action
./$program $@


