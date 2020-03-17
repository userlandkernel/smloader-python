import os
import sys
import re
import json
import requests
import pathlib
import math
import ConfigService as confsvc
import EncryptionService as encsvc

configFile = "SMLoadrConfig.json"
configService = confsvc.ConfigService(configFile)
EncryptionService = encsvc.EncryptionService()

DOWNLOAD_DIR = 'DOWNLOADS/'
PLAYLIST_DIR = 'PLAYLISTS/'
PLAYLIST_FILE_ITEMS = {}

DOWNLOAD_LINKS_FILE = 'downloadLinks.txt'
DOWNLOAD_MODE = 'single'

musicQualities = {
    'MP3_128': {
        'id': 1,
        'name': 'MP3 - 128 kbps',
        'aproxMaxSizeMb': '100'
    },
    'MP3_320': {
        'id': 3,
        'name': 'MP3 - 320 kbps',
        'aproxMaxSizeMb': '200'
    },
    'FLAC': {
        'id': 9,
        'name': 'FLAC - 1411 kbps',
        'aproxMaxSizeMb': '700'
    },
    'MP3_MISC': {
        'id': 0,
        'name': 'User uploaded song'
    }
}

selectedMusicQuality = musicQualities['MP3_320']
cliOptionDefinitions = [
    {
        'name': 'help',
        'alias': 'h',
        'description': 'Print this usage guide :)'
    },
    {
        'name': 'quality',
        'alias': 'q',
        'type': 'String',
        'defaultValue': 'MP3_320',
        'description': 'The quality of the files to download: MP3_128/MP3_320/FLAC'
    },
    {
        'name':         'path',
        'alias':        'p',
        'type':         'String',
        'defaultValue': DOWNLOAD_DIR,
        'description':  'The path to download the files to: path with / in the end'
    },
    {
        'name': 'url',
        'alias': 'u',
        'type': 'String',
        'defaultOption': True,
        'description': 'Downloads single deezer url: album/artist/playlist/profile/track url'
    },
    {
        'name': 'downloadmode',
        'alias': 'd',
        'type': 'String',
        'defaultValue': 'single',
        'description': 'Downloads multiple urls from list: "all" for downloadLinks.txt'
    }
]
cliOptions = None
isCli = len(sys.argv) > 2

unofficialApiUrl = 'https://www.deezer.com/ajax/gw-light.php'
ajaxActionUrl = 'https://www.deezer.com/ajax/action.php'
unofficialApiQueries = {
    'api_version': '1.0',
    'api_token': '',
    'input': 3
}

httpHeaders = None
requestWithoutCache = None
requestWithoutCacheAndRetry = None
requestWithCache = None

def initRequest():
    httpHeaders = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'cache-control': 'max-age=0',
        'accept-language': 'en-US,en;q=0.9,en-US;q=0.8,en;q=0.7',
        'accept-charset': 'utf-8,ISO-8859-1;q=0.8,*;q=0.7',
        'content-type': 'text/plain;charset=UTF-8',
        'cookie': 'arl=' + configService.get('arl')
    }

    requestConfig = {
        'retry': {
            'attempts': 9999999999,
            'delay': 1000, # 1 second
        },
        'defaults': {
            'headers': httpHeaders,
        }
    }
    requestWithCache = requests.Session()
    requestWithCache.headers.update(requestConfig['defaults']['headers']);
    requestWithoutCache = requests.Session()
    requestWithoutCache.headers.update(requestConfig['defaults']['headers']);
    requestConfigWithoutCacheAndRetry = {
        'defaults': {
            'headers': httpHeaders
        }
    }

unofficialApiQueries = {
	'api_version': '1.0',
	'api_token': '',
	'input': 3
}

def getDeezerUrlParts(deezerUrl):
	urlParts = deezerUrl.split("/")[-3:]
	return {
		'type': urlParts[1],
		'id': urlParts[2]
	}

def downloadMultiple(type, id):
	requestBody = None
	requestQueries = unofficialApiQueries
	if type == 'album':
		requestQueries['method'] = 'deezer.pageAlbum'
		requestBody = {
			'alb_id':'id',
			'lang':'en',
			'tab':0
		}
	elif type == 'playlist':
		requestQueries.method = 'deezer.pagePlaylist';

	elif type == 'profile':
		requestQueries.method = 'deezer.pageProfile';

	requestParams = {
		'method': 'POST',
		'url': unofficialApiUrl,
		'qs': requestQueries,
		'body': requestBody,
		'json': True,
		'jar': True
	}
	initRequest()

	request = requestWithoutCache

	if type not in ['playlist', 'profile']:
		request = requestWithCache

	request.post(requestParams['url'], params=requestParams['params'], data=requestParams['body'], type='application/json')


def startDownload(deezerUrl, downloadFromFile = False):
	deezerUrlParts = getDeezerUrlParts(deezerUrl)
	if deezerUrlParts['type'] in ['album', 'playlist', 'profile']:
		downloadMultiple(deezerUrlParts['type'], deezerUrlParts['id'])
	elif deezerUrlParts['type'] == 'artist':
		downloadArtist(deezerUrlParts['id'])
	elif deezerUrlParts['type'] == 'track':
		downloadSingleTrack(deezerUrlParts['id'])

def askForNewDownload():
	deezerUrl = input('Deezer URL: ')
	deezerUrlType = getDeezerUrlParts(deezerUrl)['type']
	allowedDeezerUrlTypes = [
                        'album',
                        'artist',
                        'playlist',
                        'profile',
                        'track'
        ]
	if deezerUrlType in allowedDeezerUrlTypes:
		startDownload(deezerUrl, False)
	return 'Deezer URL example: https://www.deezer.com/album|artist|playlist|profile|track/0123456789';



def selectDownloadMode():
	downloadMode = input('1: Single (Download single link)\n2: All    (Download all links in "' + DOWNLOAD_LINKS_FILE + '")\n\nSelect download mode: ')
	if downloadMode == '2':
		print('Do not scroll while downloading! This will mess up the UI!')
		return None
	askForNewDownload()



def selectMusicQuality():

	if isCli:

		cliHelp = cliOptions['help']
		if cliHelp or cliHelp == None:
			helpSections = []
			exit(1)

		else:
			cliUrl = cliOptions['url']
			cliQuality = cliOptions['quality']
			cliPath = cliOptions['path']
			cliDownloadMode = cliOptions['downloadMode']

			if cliQuality == 'MP3_128':
				selectedMusicQuality = musicQualities['MP3_128']
			elif cliQuality == 'MP3_320':
				selectedMusicQuality = musicQualities['MP3_320']
			elif cliQuality == 'FLAC':
				selectedMusicQuality = musicQualities['FLAC']

			DOWNLOAD_DIR = cliPath.replace('/\/$|\\$/','')
			DOWNLOAD_MODE = cliDownloadMode
			print('Do not scroll while downloading! This will mess up the UI!')

			if 'all' == DOWNLOAD_MODE:
				downloadLinksFromFile()

			elif 'single' == DOWNLOAD_MODE:
				startDownload(cliUrl)

	else:
		musicQuality = input('1: MP3  - 128  kbps\n2: MP3  - 320  kbps\n3: FLAC - 1411 kbps\n\nSelect music quality: ')
		if musicQuality == '1':
			selectedMusicQuality = musicQualities['MP3_128']
		elif musicQuality == '2':
			selectedMusicQuality = musicQualities['MP3_320']
		elif musicQuality == '3':
			selectedMusicQuality = musicQualities['FLAC']
		else:
			selectedMusicQuality = musicQualities['MP3_320']

		selectDownloadMode()

def getApiCid():
	return math.floor(1e9 * math.random())

def initDeezerCredentials():
	arl = configService.get('arl')
	if arl:
		return arl
	else:
		print('\nHow to get arl: https://git.fuwafuwa.moe/SMLoadrDev/SMLoadr/wiki/How-to-login-via-cookie\n')
		arl = input('arl cookie: ')
		configService.set('arl', str(arl))
		configService.saveConfig()
		initRequest()
		return arl

def startApp():
	initRequest()
	initDeezerCredentials()
	selectMusicQuality()

def initApp():

	print('╔══════════════════════════════════════════════════════════════════╗')
	print('║                         SMLoadr Python                           ║')
	print('╚══════════════════════════════════════════════════════════════════╝')

initApp()
startApp()
