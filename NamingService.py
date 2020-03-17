import os
import sys
import ConfigService

class NamingService:

	def __init__(self, configService):
		self.configService = configService

	def getConfig(self, type):
		return self.configService.get('naming')[type]

	def getPath(self, variables):
		name = self.getConfig('path')
		variables['albumName'] = self.getAlbumName(variables)
		for variableKey in variables:
			name = name.replace('%'+variableKey+'%',variables[variableKey])
		return name

	def getDiscPath(self, variables):
		name = self.getConfig('discPath')
		variables['name'] = self.getPath(variables)
		for variableKey in variables:
			name = name.replace('%'+variableKey+'%',variables[variableKey])
		return name

	def getAlbumName(self, variables):
		name = self.getConfig('albumName')
		for variableKey in variables:
			name = name.replace('%' + variableKey + '%', variables[variableKey])
		return name

	def getFileName(self, variables):
		name = self.getConfig('fileName')
		for variableKey in variables:
                        name = name.replace('%' + variableKey + '%', variables[variableKey])
                return name
