from booruComm import booruComm
from booruLib import booruLib
import requests, json, random

class gelbooruCaller(booruComm):
    apiToken = "&api_key=6231aca3d72f090cbd889308a4172eaec4e11ffb7490c  e3869104af5305aa0a6&user_id=430943"
    
    def __init__(self, ctx, apiToken, args):
        super().__init__(ctx, args)
        self.apicall = booruLib.apiEndpoints[booruLib.GELBOORU]
        self.instance = "GELBOORU"
        self.filteredTags = "+-loli+-amputation+-drugs+-pain+-urine+-piss+-lolicon+-shotacon+-guro+-bestiality"
        self.apiToken = apiToken

    def resolveResponse(self, extremeFilteringEnabled):
        try:
            if extremeFilteringEnabled:
                self.apicall += "200&json=1&tags="+self.tagList + self.filteredTags
            else:
                self.apicall += "200&json=1&tags="+self.tagList
            self.apicall += self.apiToken
            self.response = requests.get(self.apicall)
            self.response = self.response.json()
            responseLength = len(self.response)
            if responseLength == 0:
                self.imageReturned = False
            else:
                self.auditEntireResponse()
                self.randPost = random.randint(0, responseLength-1)
        except json.decoder.JSONDecodeError:
            self.imageReturned = False

    def setArgs(self):
        self.splitArgs()

    def makeRequest(self, extremeFilteringEnabled=False):
        self.resolveResponse(extremeFilteringEnabled)

    def getContent(self):
        content = self.resolveContent()
        return content

    