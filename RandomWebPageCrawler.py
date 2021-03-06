import requests
from random import randint
import re
class RandomWebPageCrawler(object):

    def __init__(self, startingUrlAddress, regexToFind):
        self.urlAddress = startingUrlAddress
        self.pageData = []
        self.allData = {}
        self.links = []
        self.scrapedPages = []
        self.regexToFind = regexToFind

        # large websites to begin the crawler from in case it gets stuck
        self.backupAddresses = ["www.ign.com", "www.yahoo.com", 
        "www.bing.com", "www.mashable.com", "www.medium.com", 
        "www.youtube.com", "www.adobe.com", "www.google.com", 
        "www.reddit.com", "www.wikipedia.com", "www.amazon.com",
        "www.instagram.com", "www.stackoverflow.com", "www.tmall.com", "www.twitter.com",
    "www.live.com", "www.pornhub.com", "www.twitch.tv", "www.linkedin.com",
    "www.ebay.com", "www.office.com", "www.bing.com", "www.msn.com", "www.spotify.com", 
    "www.accuweather.com", "www.samsung.com", "www.whatsapp.com", "www.xhamster.com", 
    "www.naver.com"]

    def findData(self):
        data = re.findall(self.regexToFind, self.webText)
        self.pageData = data

    def findLinks(self):
        links = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', self.webText)
        # filter some how to avoid following incorrect links
        self.links = links
    
    def crawl(self, outputToFile=False, outputPath="", verbose=False, insertIntoDB=False):
        try:
            self.getHTTPText()
        except requests.exceptions.ConnectionError:
            print("Failed to establish connection...")
            print("Terminating")
            quit()

        self.findData()

        if (outputToFile):
            self.outputFile = open(outputPath, "a")
            if self.pageData:
                for item in self.pageData:
                    print(item + " : " + self.urlAddress)
                    self.outputFile.write(item + "," + self.urlAddress + "\n")
            
            self.outputFile.close()

        if (insertIntoDB):
            if self.pageData:
                for item in self.pageData:
                    self.insertIntoDB(item, self.urlAddress)

        if (verbose):
            self.followRandomLink(verboseOutput=True)
        else:
            self.followRandomLink()

        # discard data from one page to gather new data in the next
        del self.pageData
    
    def followRandomLink(self, verboseOutput=False):
        self.findLinks()
        self.removeLinkDuplicates()
        try:
            randIndex = randint(0, len(self.links) - 1)
            self.urlAddress = self.links[randIndex]
            attemptedLink = self.urlAddress
        except ValueError:
            # No links on page. Follow backup address.
            if (verboseOutput):
                # self.outputFile.open()
                print("No links found at this address. Trying a backup url.")
                # self.outputFile.append("No links found at this address. Trying a backup url.")
                # self.outputFile.close()
            randIndex = randint(0, len(self.backupAddresses) - 1)
            self.urlAddress = self.backupAddresses[randIndex]
        try:   
            self.webText = self.getHTTPText()
            
            if (verboseOutput):
                # self.outputFile.open()
                print("Searchng: " + self.urlAddress)
                # self.outputFile.append("Searchng: " + self.urlAddress)
                # self.outputFile.close()
        except requests.exceptions.ConnectionError:
            if (verboseOutput):
                # self.outputFile.open()
                print("Connection error following link")
                print("Trying new link...")
                # self.outputFile.append("Connection error following link")
                # self.outputFile.append("Trying new link...")
                # self.outputFile.close()

            # remove link already attempted.
            self.links.remove(attemptedLink)
            # Call function again recusively.
            self.followRandomLink()

    def getHTTPText(self):
        # Remove redundant "http:// string from url"
        if (self.urlAddress.startswith("http://") or self.urlAddress.startswith("https://")):
            res = requests.get(self.urlAddress)
        else:
            res = requests.get("http://" + self.urlAddress)
        # add to scrapedPagesList to avoid scraping the same place twice
        #self.scrapedPages.append(self.urlAddress)
        self.webText = res.text

    def removeLinkDuplicates(self):
        self.links = set(self.links)
        self.links = list(self.links)

    def insertIntoDB(self, data, fromWebsite):
        # overload this method in a subclass
        # connect to DB and insert data into in + where it came from
        pass



# # pageCrawler will find email addresses. 
# REGEX TO FIND EMAIL ADDRESSES
# pageCrawler = RandomWebPageCrawler("www.achieve3000.com/contact-us/", r'[\w\.-]+@[\w\.-]+')
# while True:
#     pageCrawler.crawl(outputToFile=True, outputPath="output.csv", verbose=True, insertIntoDB=True)
