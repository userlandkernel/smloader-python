# Helper class for loading and storing preferences
import os
import sys
import json
import requests

class ConfigService:

	def __init__(self, configFile = None):
		self.configFile = configFile
		self.config = {
			"naming":{
				"path": "DOWNLOADS/%artist%/%albumName%",
				"discPath": "%path%/Disc %disc%",
				"albumName": "%album% (%type%)",
				"fileName": "%number% %title%"
			},
			"arl":""
		};
		self.loadConfig()
		self.saveConfig()


	def loadConfig(self):
		configFileContent = self.configFile
		try:
			configFileContent = open(configFileContent, 'r+').read()
			configFileContent = json.loads(configFileContent)
		except Exception as e:
			return self.config

		for key, value in configFileContent.items():
			self.config[key] = value

		return self.config

	def saveConfig(self):
		open(self.configFile, 'w').write(json.dumps(self.config, sort_keys=True, indent=4))


	def set(self, key, value):
		self.config[key] = value


	def get(self, key):

		if key == None:
			return self.config

		return self.config[key]
