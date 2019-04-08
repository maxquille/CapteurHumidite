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
from I2C_SW_CLS import *
import subprocess 
from collections import defaultdict

loggerScript_path = "/home/pi/Dev/CapteurHumidite/logs/logger_capteurHum.log"
recordValue_path = "/home/pi/HumidityValue/RecordValue.log"

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
		self.log = logging.getLogger(__name__) 
	
	def create(self):
		""" Logger path """ 
		self.pathlogger = recordValue_path

		""" Logger setting """
		self.log.setLevel(logging.DEBUG)
		self.file_handler = RotatingFileHandler(os.path.normpath(self.pathlogger), 'a', maxBytes=5000000, backupCount=100) # 5000000 = 5Mo
		self.log.addHandler(self.file_handler)
		#self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		#self.file_handler.setLevel(logging.DEBUG)
		#self.file_handler.setFormatter(self.formatter)
		#self.log.addHandler(self.file_handler)

	
	def info(self, string):
		self.log.info(string)
	
	def warning(self, string):
		self.log.warning(string)
	
	def error(self, string):
		self.log.error(string)
	
	def debug(self, string):
		self.log.debug(string)	
		
def main_loop(log_script,log_recordValue):
	seq = 0
	i = 0
	dict_ValuesAllCapteurs = defaultdict(list)
	for j in range(0,8):
		dict_ValuesAllCapteurs[j] = {}
		dict_ValuesAllCapteurs[j]['pressure'] = 255
		dict_ValuesAllCapteurs[j]['humidity'] = 255
		dict_ValuesAllCapteurs[j]['temperature'] = 255
	
	while True:
		
		if (i == 0) or (i == 1) or (i == 5) or (i == 6):
			
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
					log_script.error("Error reading all values ch" + str(i))
						
				time.sleep(1)
				
			except:
				log_script.error("Impossible switch to ch" + str(i))
			
		i += 1
		
		if i == 8:

			# Record Value
			chaine = ""
			for j in range(0,8):
				chaine += str(j) + ';' + str(dict_ValuesAllCapteurs[j]['pressure']).replace('.',',') + ' ' + str(j) + ';' + str(dict_ValuesAllCapteurs[j]['humidity']).replace('.',',') + ' ' + str(j) + ';' + str(dict_ValuesAllCapteurs[j]['temperature']).replace('.',',') + ' '
			
			log_recordValue.info(str(seq) + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + chaine)
			
			# Reset value
			for j in range(0,8):
				dict_ValuesAllCapteurs[j] = {}
				dict_ValuesAllCapteurs[j]['pressure'] = 255
				dict_ValuesAllCapteurs[j]['humidity'] = 255
				dict_ValuesAllCapteurs[j]['temperature'] = 255
			
			seq += 1
			i = 0
			time.sleep(5)
			
		
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
	
	log_recordValue.info("Nouvelle sessions : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	
	#args = parse_args()
	#name_parameter_file= args.parameter
	#retrieve_parameters(log_script,name_parameter_file)

	main_loop(log_script,log_recordValue)

		
if __name__ == "__main__":
	main()


