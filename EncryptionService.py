# TODO: Actually implement
import os
import sys
import crypto

class EncryptionService:

	def __init__(self):
		return

	def getSongFileName(trackInfos, trackQuality):
		step1 = [trackInfos.MD5_ORIGIN, trackQuality, trackInfos.SNG_ID, trackInfos.MEDIA_VERSION].join('¤')
		return None

	def getBlowfishKey(trackInfos):
		SECRET = 'g4el58wc0zvf9na1'
		idMd5 = None
		bfKey = ''
		for i in range(0, 16):
			bfKey += ''
		return bfKey
