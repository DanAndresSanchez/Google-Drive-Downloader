import io
import os
import os.path
import sys
import json
import pandas as pd
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload, MediaDownloadProgress
from gDrive_calculator import getSize

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

global service
service = None

download_path = './Downloaded Files'
original_path = './Downloaded Files'

global folder_data
folder_data = None

global files_downloaded
files_downloaded = 0

global amount_downloaded
amount_downloaded = 0

global extension
extension = ''


def getFilesDownloaded():
    global files_downloaded
    return files_downloaded

def getAmountDownloaded():
    global amount_downloaded
    return amount_downloaded

def getFolderData():
    global folder_data, files_downloaded
    if folder_data is not None:
        return files_downloaded / folder_data['files']
    return -1

def getDriveId():
    global service, folder_data
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    file_metadata = {
        'name': 'temporary folder - D3l3Te m#',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    tempFolderId = service.files().create(body=file_metadata, fields='id').execute()[
        "id"]  # Create temporary folder
    myDriveId = service.files().get(fileId=tempFolderId, fields='parents').execute()[
        "parents"][0]  # Get parent ID
    service.files().delete(fileId=tempFolderId).execute()  # Delete temporary folder
    folder_data = getSize(myDriveId, service)
    return myDriveId


def setPath(path):
    global download_path, original_path
    original_path = path
    download_path = path


def downloadDrive(path):
    global drive_id, download_path, original_path, service
    drive_id = getDriveId()
    setPath(path)
    downloadFolder('', drive_id, download_path, service)
    if os.path.isdir('/temporary folder'):
        os.rmdir(original_path + '/temporary folder')
    print('Finished downloading the drive!')


def downloadFolder(folder_name, folder_id, path, service):
    print(path + ':')
    global download_path
    global original_path
    download_path = path
    if not os.path.isdir(download_path):
        os.mkdir(download_path)
    query = f"parents = '{folder_id}'"
    results = service.files().list(
        q=query, fields="nextPageToken, files(id, name, mimeType, size)").execute()
    items = results.get('files', [])
    if not items:
        print('\tEmpty Folder!')
        download_path = path.rsplit('/', 1)[0]
        if download_path == '.' or download_path == '' or download_path == '/':
            download_path = original_path
    else:
        for item in items:
            if 'size' in item:
                print(u'\t{0} | {1} | {2} | {3}'.format(
                    item['name'], item['id'], item['mimeType'], item['size']))
                downloadFileSize(item['id'], item['name'],
                             item['mimeType'], item['size'], download_path, service)
            else:
                print(u'\t{0} | {1} | {2}'.format(
                    item['name'], item['id'], item['mimeType']))
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    downloadFolder(item['name'], item['id'],
                                download_path + '/' + item['name'], service)
                else:
                    # print(item['name'])
                    downloadFile(item['id'], item['name'],
                                item['mimeType'], download_path, service)
        download_path = path.rsplit('/', 1)[0]
        if download_path == '.' or download_path == '' or download_path == '/':
            download_path = original_path


def downloadFileSize(file_id, file_name, file_type, file_size, path, service):
    global folder_data, extension, files_downloaded, amount_downloaded
    request = getFile(file_id, file_type, service)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    # To get download progress for file
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print(u'Download %{0}'.format(int(status.progress() * 100)))

    # Update bar
    amount_downloaded = amount_downloaded + int(file_size)
    print(u'\t\t{0} {1} '.format(str(round((amount_downloaded / folder_data['bytes']) * 100, 2)), '% Done by size'))
    files_downloaded = files_downloaded + 1
    print(u'\t\t{0} {1} '.format(str(round((files_downloaded / folder_data['files']) * 100, 2)), '% Done by count'))

    fh.seek(0)
    with open(os.path.join(path, file_name + extension), 'wb') as f:
        f.write(fh.read())
        f.close()


def downloadFile(file_id, file_name, file_type, path, service):
    global folder_data, extension, files_downloaded
    request = getFile(file_id, file_type, service)
    if request == None:
        return
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    # To get download progress for file
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print(u'Download %{0}'.format(int(status.progress() * 100)))

    # Update bar
    files_downloaded = files_downloaded + 1
    print(u'\t\t{0} {1} '.format(str(round((files_downloaded / folder_data['files']) * 100, 2)), '% Done by count'))

    fh.seek(0)
    with open(os.path.join(path, file_name + extension), 'wb') as f:
        f.write(fh.read())
        f.close()


def getFile(file_id, file_type, service):
    global extention
    if file_type == 'application/vnd.google-apps.document':
        # print('Google Doc')
        extention = '.docx'
        request = service.files().export_media(
            fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    elif file_type == 'application/vnd.google-apps.spreadsheet':
        # print('Google Sheet')
        extention = '.xlsx'
        request = service.files().export_media(
            fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    elif file_type == 'application/vnd.google-apps.presentation':
        # print('Google Slide')
        extention = '.pptx'
        request = service.files().export_media(
            fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    elif file_type == 'application/vnd.google-apps.form':
        return
    elif file_type == 'application/vnd.google-apps.map':
        return
    elif file_type == 'application/vnd.google-apps.site':
        return
    else:
        request = service.files().get_media(fileId=file_id)
    return request