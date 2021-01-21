import io
import os
import os.path
import sys
import pandas as pd
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload, MediaDownloadProgress

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

global service
service = None
#response = service.files().list().execute()
download_path = './Downloaded Files'
original_path = './Downloaded Files'
total_size = 0


def getDriveId():
    global service
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


def downloadFile(file_id, file_name, file_type, path, service):
    extention = ''
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
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    # To get download progress for file
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print(u'Download %{0}'.format(int(status.progress() * 100)))

    fh.seek(0)
    with open(os.path.join(path, file_name + extention), 'wb') as f:
        f.write(fh.read())
        f.close()


def downloadFolder(folder_name, folder_id, path, service):
    print(path + ':')
    global download_path
    global original_path
    download_path = path
    if not os.path.isdir(download_path):
        os.mkdir(download_path)
    query = f"parents = '{folder_id}'"
    results = service.files().list(
        q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    if not items:
        print('\tEmpty Folder!')
        download_path = path.rsplit('/', 1)[0]
        if download_path == '.' or download_path == '' or download_path == '/':
            download_path = original_path
    else:
        for item in items:
            print(u'\t{0} | {1} | {2}'.format(
                item['name'], item['id'], item['mimeType']))
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                downloadFolder(item['name'], item['id'],
                               download_path + '/' + item['name'], service)
                # Need to be able to come back out from folder to original place
                # Maybe get root folder and recursivly call function for all files
            else:
                # print(item['name'])
                downloadFile(item['id'], item['name'],
                             item['mimeType'], download_path, service)
        download_path = path.rsplit('/', 1)[0]
        if download_path == '.' or download_path == '' or download_path == '/':
            download_path = original_path
