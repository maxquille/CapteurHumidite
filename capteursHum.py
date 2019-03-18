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
from logging.handlers import RotatingFileHandler
from I2C_SW_CLS import *

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
		self.file_handler = RotatingFileHandler(os.path.normpath(self.pathlogger), 'a', maxBytes=5000000, backupCount=1000) # 5000000 = 5Mo
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
	i = 0
	while True:
		
		try:
			if (i == 0) or (i == 1) or (i == 5) or (i == 6):
				print "Switch to chn:" + str(i)
				SW.chn(i)
				os.system("read_bme280")
				time.sleep(3)
			
		except:
			print "pas marche"
			
		i += 1
		if i == 8:
			i = 0
			
		
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

	#args = parse_args()
	#name_parameter_file= args.parameter
	#retrieve_parameters(log_script,name_parameter_file)

	main_loop(log_script,log_recordValue)

		
if __name__ == "__main__":
	main()


