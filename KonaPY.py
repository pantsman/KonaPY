import requests, json, time, urllib, hashlib, argparse
from pathlib import Path

###GLOBAL VARIABLES DO NOT CHANGE###
outputDirectory=None
baseUrl='https://konachan.com/post.json'
basePath=None
localHashes = {}

def errorReporting(errorCode):
    if errorCode == 403:
        return 'Error 403 received Access Denied Ending Script'
    elif errorCode == 404:
        return 'Error 404 received Not Found Ending Script'
    elif errorCode == 421:
        return 'Error 421 received User Throttled Ending Script'
    elif errorCode == 424:
        return 'Error 424 received Invalid Parameters Ending Script'
    elif errorCode == 500:
        return 'Error 500 received An Unknown Error Occured on the Remote Server Ending Script'
    elif errorCode == 503:
        return 'Error 503 received Remote Service Cannot Handle the Request Ending Script'
    else:
        return 'Error {0} Received Ending Script'.format(errorCode)

def healDirectory(outputDirectory, tags):
    baseTags='?tags='+'%20'.join(tags)
    page=1
    localHashes = {}

    #Generate hashes for all files in the directory
    for item in Path(outputDirectory).iterdir():
        #Checks if not a directory before hasing
        if item.is_dir() == False:
            #Opens file as a binary to hash
            with open(item, 'rb') as localImage:
                imageHash = hashlib.md5(localImage.read()).hexdigest()
                localHashes[imageHash] = item
    #Using the provided tag search for all images
    while True:
        #Forms request
        konaRequest = requests.get('{0}{1}&page={2}'.format(baseUrl,baseTags,page))
        #If request is not valid return error code and break loop
        if konaRequest.status_code != 200:
            print(errorReporting(konaRequest.status_code))
            break 
        #Break loop if no objects returned but request is good
        elif len(konaRequest.json()) <= 0:
            break
        #Print current page of results to screen
        #For each image in the returned request check if hash exists matches a file
        for konaImage in konaRequest.json():
            #Checks for matching hash
            if konaImage['md5'] in localHashes:
                #Generates file path for renaming
                newFile = Path('{0}/Konachan - {1}.{2}'.format(outputDirectory,konaImage['id'],konaImage['file_url'].split('.')[-1]))
                #Checks if local file exists to avoid missing file error
                if localHashes[konaImage['md5']].exists():
                    #Checks if there is file already named the same as the generated name
                    if newFile.exists() == False:
                        #Could not use path from dictionary assigns to variable for use
                        oldFile = localHashes[konaImage['md5']]
                        #Renames file
                        oldFile.rename(newFile)
        #Pause run to avoide being blocked
        time.sleep(1)
        #Go to next page
        page += 1

def downloadImages(outputDirectory, ratings, tags):
    baseTags='?tags='+'%20'.join(tags)
    page=1

    while True:
        konaRequest = requests.get('{0}{1}&page={2}'.format(baseUrl,baseTags,page))
        if konaRequest.status_code != 200:
            print(errorReporting(konaRequest.status_code))
            break 
        elif len(konaRequest.json()) <= 0:
            break
        print('Processing Page: {0}'.format(page))
        for konaImage in konaRequest.json():
            if konaImage['rating'] in ratings:
                localFile = Path('{0}/Konachan - {1}.{2}'.format(outputDirectory,konaImage['id'],konaImage['file_url'].split('.')[-1]))
                print(localFile)
                localMd5 = None
                if localFile.exists() == True:
                    with open(localFile, 'rb') as localImage:
                        localMd5 = hashlib.md5(localImage.read()).hexdigest()
                if konaImage['md5'] != localMd5:
                    print('downloading new file {0} rating: {1}'.format(localFile,konaImage['rating']))
                    urllib.request.urlretrieve(konaImage['file_url'], localFile)
                    time.sleep(1)
        page += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='KonaPY',description='A Command Line Tool for Konachan Written in Python')
    parser.add_argument('--tags', metavar='tags', nargs='+',
                        help='Tags to search for seperated by spaces')
    parser.add_argument('--ratings', metavar='ratings', nargs='*', default='[s]',
                        help='Ratings to be allow seperated by spaces. Only safe images allowed by default')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--heal', action='store_true')
    group.add_argument('--download', action='store_true')
    group.add_argument('--delewd', action='store_true')

    args = parser.parse_args()

    outputDirectory = input('Please enter a directory:')

    if args.heal == True:
        healDirectory(outputDirectory, args.tags)
    elif args.download == True:
        downloadImages(outputDirectory, args.ratings, args.tags)
    elif args.delewd == True:
        delewd()  