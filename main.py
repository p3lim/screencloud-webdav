import os
import re
import ScreenCloud

from http.client import HTTPSConnection
from base64 import b64encode

from PythonQt.QtCore import QSettings, QFile, QStandardPaths
from PythonQt.QtGui import QFileDialog
from PythonQt.QtUiTools import QUiLoader

import re
def fix_filename(name):
	# temp fix until 1.3.1 gets released
	pattern = re.compile("^b'(.*)'(\.%s)$" % ScreenCloud.getScreenshotFormat())
	match = pattern.match(name)
	return match and ''.join(match.groups()) or name

from hashlib import md5
def get_rnd_dict():
	# adds {rnd_1} through {rnd_20} for abbrevated hashes to use as replacements in file names
	h = md5(os.urandom(129)).hexdigest()
	return {'rnd_%s' % n: h[:n] for n in range(1,20)}

class WebDAV(object):
	def __init__(self, url, username=None, password=None):
		# TODO: validate args
		self.connection = HTTPSConnection(url)
		self.connection.close()
		self.headers = {}

		if username and password:
			self.auth(username, password)

	def auth(self, username, password):
		# TODO: validate args
		auth = b64encode(bytes(username + ':' + password, 'ascii')).decode('ascii')
		self.headers['Authorization'] = 'Basic %s' % auth

	def exists(self, path):
		# TODO: validate args
		response = self._request('GET', path)
		return response.status == 200

	def upload(self, path, file_path):
		# TODO: validate args
		# if not name:
		if self.exists(path):
			return False

		if not os.path.isfile(file_path):
			return False

		with open(file_path, 'rb') as file:
			response = self._request('PUT', path, file.read())
			return response.status == 201

	def mkdir(self, path):
		# TODO: validate args
		if self.exists(path):
			return False

		response = self._request('MKCOL', path)
		return response.status

	def _request(self, method, path, file=None):
		if path[0] != '/':
			# account for stupidity
			path = '/' + path

		self.connection.connect()
		self.connection.request(method, path, file, headers=self.headers)
		response = self.connection.getresponse()
		self.connection.close()
		return response

class WebDAVUploader():
	def __init__(self):
		self.uil = QUiLoader()
		self.loadSettings()

		# self.dav_address = 'myfiles.fastmail.com'

	def upload(self, screenshot, name):
		name = fix_filename(name)
		path = self.save(screenshot, name)

		if not path:
			ScreenCloud.setError('Failed to save screenshot')
			return False

		dav = WebDAV(self.dav_address)
		dav.auth(self.username, self.password)

		if not dav.exists('ScreenCloud'):
			dav.mkdir('ScreenCloud')

		print(name)

		if not dav.upload('ScreenCloud/' + name, path):
			ScreenCloud.setError('Failed to upload screenshot')
			return False

		if self.copy_link:
			ScreenCloud.setUrl(self.host_address + '/' + name)

		return True

	def save(self, screenshot, name, path=None):
		if self.save_file and len(self.save_path) > 0:
			if os.path.isdir(self.save_path):
				path = self.save_path
			# else: # TODO: warn the user that the file could not be saved locally

		if not path:
			path = QStandardPaths.writableLocation(QStandardPaths.TempLocation)

		path = os.path.join(path, name)

		try:
			screenshot.save(QFile(path), ScreenCloud.getScreenshotFormat())
		except Exception as e:
			raise

		return path

	def getFilename(self):
		return fix_filename(ScreenCloud.formatFilename(self.name_format, custom_vars=get_rnd_dict()))

	def showSettingsUI(self, parentWidget):
		self.parentWidget = parentWidget

		self.settingsDialog = self.uil.load(QFile(workingDir + '/settings.ui'), parentWidget)
		self.settingsDialog.group_url.check_copylink.connect('stateChanged(int)', self.updateUI)
		self.settingsDialog.group_screenshot.input_name.connect('textChanged(QString)', self.nameFormatEdited)
		self.settingsDialog.group_screenshot.check_savefile.connect('stateChanged(int)', self.updateUI)
		self.settingsDialog.group_screenshot.button_browse.connect('clicked()', self.browseForDirectory)
		self.settingsDialog.connect('accepted()', self.saveSettings)

		self.loadSettings()

		self.settingsDialog.group_url.input_url.text = self.dav_address
		self.settingsDialog.group_url.input_username.text = self.username
		self.settingsDialog.group_url.input_password.text = self.password
		self.settingsDialog.group_url.check_copylink.checked = self.copy_link
		self.settingsDialog.group_url.input_public.text = self.host_address

		self.settingsDialog.group_screenshot.input_name.text = self.name_format
		self.settingsDialog.group_screenshot.check_savefile.checked = self.save_file
		self.settingsDialog.group_screenshot.input_directory.text = self.save_path

		self.updateUI()
		self.settingsDialog.open()

	def loadSettings(self):
		settings = QSettings()
		settings.beginGroup('uploaders')
		settings.beginGroup('webdav')

		self.dav_address = settings.value('url', '')
		self.username = settings.value('username', '')
		self.password = settings.value('password', '')
		self.copy_link = settings.value('copy-link', 'True') == 'True'
		self.host_address = settings.value('host-address', '')

		self.name_format = settings.value('name-format', '%Y-%m-%d_%H-%M-%S')
		self.save_file = settings.value('save-file', 'False') == 'True'
		self.save_path = settings.value('save-path', '')

		settings.endGroup()
		settings.endGroup()

	def saveSettings(self):
		settings = QSettings()
		settings.beginGroup('uploaders')
		settings.beginGroup('webdav')

		settings.setValue('url', self.settingsDialog.group_url.input_url.text)
		settings.setValue('username', self.settingsDialog.group_url.input_username.text)
		settings.setValue('password', self.settingsDialog.group_url.input_password.text)
		settings.setValue('copy-link', str(self.settingsDialog.group_url.check_copylink.checked))
		settings.setValue('host-address', self.settingsDialog.group_url.input_public.text)

		settings.setValue('name-format', self.settingsDialog.group_screenshot.input_name.text)
		settings.setValue('save-file', str(self.settingsDialog.group_screenshot.check_savefile.checked))
		settings.setValue('save-path', self.settingsDialog.group_screenshot.input_directory.text)

		settings.endGroup()
		settings.endGroup()

	def isConfigured(self):
		self.loadSettings()
		return len(self.dav_address) > 0 and len(self.username) > 0 and len(self.password) > 0

	def browseForDirectory(self):
		path = QFileDialog.getExistingDirectory(self.settingsDialog, 'Select location', self.save_path)
		if path:
			self.settingsDialog.group_screenshot.input_directory.setText(path)
			self.saveSettings()

	def nameFormatEdited(self, name_format):
		self.settingsDialog.group_screenshot.label_example.setText(fix_filename(ScreenCloud.formatFilename(name_format, custom_vars=get_rnd_dict())))

	def updateUI(self):
		save_file = self.settingsDialog.group_screenshot.check_savefile.checked
		self.settingsDialog.group_screenshot.label_directory.setVisible(save_file)
		self.settingsDialog.group_screenshot.input_directory.setVisible(save_file)
		self.settingsDialog.group_screenshot.button_browse.setVisible(save_file)

		copy_link = self.settingsDialog.group_url.check_copylink.checked
		self.settingsDialog.group_url.label_public.setVisible(copy_link)
		self.settingsDialog.group_url.input_public.setVisible(copy_link)
