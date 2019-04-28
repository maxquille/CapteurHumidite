#! /usr/bin/python
# -*- coding: utf-8 -*-
# 
# File: 
#	capteurHum.py
# 
# Description:
# 	
# 
# 
# Ex:
#	capteurHum.py
#
# MQ 18/03/2019
#

import os, time, logging, sys
from datetime import datetime
from time import strftime
from logging.handlers import RotatingFileHandler
import subprocess 
from collections import defaultdict
import RPi.GPIO as GPIO

loggerScript_path = "/home/pi/Dev/CapteurHumidite/logs/logger_capteurHum.log"
recordValue_path = "/home/pi/HumidityValue/RecordValue.log"

seq = 0
failed_select_chn = 0
dict_ValuesAllCapteurs = defaultdict(list)

""" Init GPIO RST Multiplexer"""
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(8, GPIO.OUT) #RST multipexer
GPIO.output(8,True)

""" Import I2C_SW_CLS """
try:
	from I2C_SW_CLS import *
except:
	print("Error, impossible to load I2C_SW_CLS")
	sys.exit()
		
""" Create logger class """
class logger_script(object):
	def __init__(self):
		self.log = logging.getLogger(__name__) 
	
	def create(self):
		""" Logger path """ 
		self.pathlogger = loggerScript_path

		""" Logger setting """
		self.log.setLevel(logging.DEBUG)
		self.file_handler = RotatingFileHandler(os.path.normpath(self.pathlogger), 'a', 1000000, 5)
		self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		self.file_handler.setLevel(logging.DEBUG)
		self.file_handler.setFormatter(self.formatter)
		self.log.addHandler(self.file_handler)
		self.gsteam_handler = logging.StreamHandler() # création d'un second handler qui va rediriger chaque écriture de log sur la console
		self.gsteam_handler.setFormatter(self.formatter)
		self.gsteam_handler.setLevel(logging.DEBUG)
		self.log.addHandler(self.gsteam_handler)
	
	def info(self, string):
		self.log.info(string)
	
	def warning(self, string):
		self.log.warning(string)
	
	def error(self, string):
		self.log.error(string)
	
	def debug(self, string):
		self.log.debug(string)	

""" Create logger record value class """
class logger_recordValue(object):
	def __init__(self):
		self.log = logging.getLogger("RecordValue") 
	
	def create(self):
		""" Logger path """ 
		self.pathlogger = recordValue_path

		""" Logger setting """
		self.log.setLevel(logging.DEBUG)
		self.file_handler = RotatingFileHandler(os.path.normpath(self.pathlogger), 'a', maxBytes=5000000, backupCount=100) # 5000000 = 5Mo
		self.log.addHandler(self.file_handler)
		self.formatter = logging.Formatter('%(message)s')
		self.file_handler.setLevel(logging.DEBUG)
		self.file_handler.setFormatter(self.formatter)

	
	def info(self, string):
		self.log.info(string)
	
	def warning(self, string):
		self.log.warning(string)
	
	def error(self, string):
		self.log.error(string)
	
	def debug(self, string):
		self.log.debug(string)	

def read_value(log_script):
	global failed_select_chn
	global dict_ValuesAllCapteurs
	
	# Reset Value
	for j in range(0,8):
		if j not in dict_ValuesAllCapteurs:
			dict_ValuesAllCapteurs[j] = {}
		dict_ValuesAllCapteurs[j]['pressure'] = 255
		dict_ValuesAllCapteurs[j]['humidity'] = 255
		dict_ValuesAllCapteurs[j]['temperature'] = 255
	
	
	# Retreive value from 8 sensors
	for i in range (0,8):
		if i <= 5:
			try:
				SW.chn(i)
				x = subprocess.Popen(["read_bme280"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				res = x.stdout.read().strip().split('\n')
				if len(res) == 3:
					if res[0].find("hPa") != 0:
						temp = res[0].strip().split("hPa")
						temp = temp[0].strip()
						dict_ValuesAllCapteurs[i]['pressure'] = temp
						
					else:
						log_script.error("Error reading pressure value ch" + str(i))
					
					if res[1].find("%") != 0:
						temp = res[1].strip().split("%")
						temp = temp[0].strip()
						dict_ValuesAllCapteurs[i]['humidity'] = temp
						
					else:
						log_script.error("Error reading humidity value ch" + str(i))
					
					if res[2].find("C") != 0:
						temp = res[2].strip().split("C")
						temp = temp[0].strip()
						dict_ValuesAllCapteurs[i]['temperature'] = temp
						
					else:
						log_script.error("Error reading temperature value ch" + str(i))
					
					"""print "hPa", dict_ValuesAllCapteurs[i]['pressure']
					print "humidity", dict_ValuesAllCapteurs[i]['humidity']
					print "temperature", dict_ValuesAllCapteurs[i]['temperature']"""

				else:
					log_script.error("Error reading values from ch" + str(i))	
					time.sleep(1)
				
			except:
				log_script.error("Impossible switch to ch" + str(i))
				failed_select_chn += 1

	if failed_select_chn == 5:
		restart_multiplerI2C(log_script)
		failed_select_chn = 0
	
def record_value(log_recordValue):
	global seq
	global dict_ValuesAllCapteurs
	
	# Record Value
	chaine = ""
	for j in range(0,8):
		chaine += str(j) + ';' + str(dict_ValuesAllCapteurs[j]['pressure']).replace('.',',') + ' ' + str(j) + ';' + str(dict_ValuesAllCapteurs[j]['humidity']).replace('.',',') + ' ' + str(j) + ';' + str(dict_ValuesAllCapteurs[j]['temperature']).replace('.',',') + ' '
	
	log_recordValue.info(str(seq) + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + chaine)
	seq += 1

def restart_multiplerI2C(log_script):
	GPIO.output(8,False)
	time.sleep(2)
	GPIO.output(8,True)
	log_script.warning("Restart multiplexer I2C")
	
def main_loop(log_script,log_recordValue):
	while True:
		read_value(log_script)
		record_value(log_recordValue)
		
		time.sleep(300) # Tempo entre boucle
			
def auto_test(log_script):
	GPIO.output(40,True) # VMC petite vitesse
	GPIO.output(38,True) # VMC ON
	time.sleep(3)
	GPIO.output(38,False) # VMC OFF
	time.sleep(3)
	GPIO.output(40,False) # VMC grande vitesse
	GPIO.output(38,True) # VMC ON
	time.sleep(3)
	GPIO.output(40,True) # VMC petite vitesse
	GPIO.output(38,False) # VMC OFF
	
	log_script.info("AutoTest VMC Done")
	
def main():
	""" 
		Main
	"""

	""" Create logger script """
	log_script = logger_script()
	log_script.create()
	log_script.info("")
	log_script.info("")
	log_script.info("********************")
	log_script.info("*** Start script ***")
	log_script.info("********************")
	
	log_recordValue = logger_recordValue()
	log_recordValue.create()
	
	""" Script argument """
	if len(sys.argv) != 1:
		log_script.error("Error, argument not valid")
		sys.exit()
	
	""" Header record value file """
	log_recordValue.info("Nouvelle sessions : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	
	""" Init GPIO Module Relay"""
	GPIO.setup(31, GPIO.OUT) #Relay IN1 => Registre 1
	GPIO.setup(32, GPIO.OUT) #Relay IN2 => Registre 2
	GPIO.setup(33, GPIO.OUT) #Relay IN3 => Registre 3
	GPIO.setup(35, GPIO.OUT) #Relay IN4 => Registre 4
	GPIO.setup(36, GPIO.OUT) #Relay IN5 => Registre 5
	GPIO.setup(37, GPIO.OUT) #Relay IN6 => Alim registre
	GPIO.setup(38, GPIO.OUT) #Relay IN7 => ON/OFF VMC 
	GPIO.setup(40, GPIO.OUT) #Relay IN8 => petite / grande vitesse VMC
	
	""" Restart multiplexer """
	restart_multiplerI2C(log_script)

	""" Auto test VMC """
	auto_test(log_script)
	
	""" Init GPIO value """
	GPIO.output(31,True)	# False Cmd Registre en ouverture		True Cmd Registre en fermeture
	GPIO.output(32,True)
	GPIO.output(33,True)
	GPIO.output(35,True)
	GPIO.output(36,True)	
	GPIO.output(37,True)	# False Alim registre sous tension		True Alim registre hors tension	
	GPIO.output(40,True) 	# False VMC grande vitesse				True VMC petite vitesse
	GPIO.output(38,True) 	# False VMC eteinte						True VMC allumee
	
	main_loop(log_script,log_recordValue)

		
if __name__ == "__main__":
	main()


