import requests, json, time, urllib, hashlib, argparse
from pathlib import Path

def errorReporting(errorCode):
    if konaRequest.status_code == 403:
        return 'Error 403 received Access Denied Ending Script'
    elif konaRequest.status_code == 404:
        return 'Error 404 received Not Found Ending Script'
    elif konaRequest.status_code == 421:
        return 'Error 421 received User Throttled Ending Script'
    elif konaRequest.status_code == 424:
        return 'Error 424 received Invalid Parameters Ending Script'
    elif konaRequest.status_code == 500:
        return 'Error 500 received An Unknown Error Occured on the Remote Server Ending Script'
    elif konaRequest.status_code == 503:
        return 'Error 503 received Remote Service Cannot Handle the Request Ending Script'
    else:
        return 'Error {0] Received Ending Script'.format(errorCode)

def generateFolder(outputDirectory):
    if outputDirectory == None:
        outputDirectory = './konachan/'
        if Path(outputDirectory).exists() == False:
            with Path(outputDirectory) as tempPath:
                tempPath.mkdir()
    else:
        while Path(outputDirectory).exists() == False:
            outputDirectory = input('Invalid path enter a new one:')
        with Path(outputDirectory) / 'konachan' as tempPath:
            if tempPath.exists() == False:
                tempPath.mkdir()
            outputDirectory = tempPath.resolve()
    return outputDirectory

def downloadImages(outputDirectory, konaJson, ratings):
    if konaJson['rating'] in ratings:
        localFile = Path('{0}/Konachan - {1}.{2}'.format(outputDirectory,konaJson['id'],konaJson['file_url'].split('.')[-1]))
        print(localFile)
        localMd5 = None
        if localFile.exists() == True:
            with open(localFile, 'rb') as localImage:
                localMd5 = hashlib.md5(localImage.read()).hexdigest()
        if konaJson['md5'] != localMd5:
            print('downloading new file {0} rating: {1}'.format(localFile,konaJson['rating']))
            urllib.request.urlretrieve(konaJson['file_url'], localFile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A Command Line Tool for Konachan Written in Python')
    parser.add_argument('--tags', metavar='tags', nargs='+',
                        help='Tags to search for seperated by spaces')
    parser.add_argument('--ratings', metavar='ratings', nargs='*', default='[s]',
                        help='Ratings to be allow seperated by spaces. Only safe images allowed by default')

    args = parser.parse_args()

    outputDirectory=None
    baseUrl='https://konachan.com/post.json'
    baseTags='?tags='+'%20'.join(args.tags)
    page=1
    basePath=None

    outputDirectory = input('Please enter a directory:')

    outputDirectory = generateFolder(outputDirectory)

    while True:
        konaRequest = requests.get('{0}{1}&page={2}'.format(baseUrl,baseTags,page))
        if konaRequest.status_code != 200:
            print(errorReporting(konaRequest.status_code))
            break 
        elif len(konaRequest.json()) <= 0:
            break
        print('Processing Page: {0}'.format(page))
        for konaImage in konaRequest.json():
            downloadImages(outputDirectory,konaImage,args.ratings)
            time.sleep(1)
        page += 1       