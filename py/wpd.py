import json
import time
import requests
from urllib.request import urlopen
from os.path import join


class pd():
    def __init__(self):
        self.prodlist = {}
        self.brandlist = {}

    def findbrands(self, url):
        g = urlopen(url)  # opening the site map page
        f = g.read()  # using the read function to extract the contents of the html request
        g.close()  # close the file to save memory and prevent a memory leak

        f = str(f)  # .read() returns a binary value, this converts it to a string
        print("Downloading brand list")
        firstbrand = "/1000-mile"
        lastbrand = "/zoot"
        tempbrands = f[f.find(firstbrand)-1:f.find(lastbrand)+21]
        tempbrands = tempbrands.split('<li>')  # split the string into the separate brands using '"'
        for brand in tempbrands:
            if "http://www.wiggle.co.uk/" in brand:  # is used to identify the brands as they are links to the page
                brandurl = brand[9:brand.find('">')]  # remove the "/" from the brand name
                brandname = brand[brand.find('/">')+3:brand.find('</a></li>')]
                self.prodlist[brandname] = []  # add the brand key to the product list
                self.brandlist[brandname] = brandurl
        print("Brand list done!")

    def findproducts(self, url):
        for brand in self.brandlist:
            print("Downloading brand:", brand)
            x = 1
            g = requests.get(self.brandlist[brand], params={"g":str(x), "ps":"96"}, timeout=30)
            g.raise_for_status()
            f = g.text
            pagestr = str(f)
            pagestr = pagestr.replace(" ", "")
            pagelist = pagestr.split('\r\n')  # splits the page into a list rather than one long string, making some
            # methods easier later on
            pagelist = pagelist[pagelist.index('<divid="product-list">'):
            pagelist.index('<divclass="bem-footer"data-page-area="Footer">')]  # slice the list to remove unnecessary
            # content, from one of the top elements to one just underneath the products
            while pagelist.count('<divid="Empty-Results">') == 0:
                while pagelist.count('<divclass="bem-product-thumb--grid">') > 0:  # check there are still unprocessed
                    # products in the page
                    for line in pagelist:
                        if "bem-product-thumb__name--grid" in line:
                            produrl = line[45:line.find('"data-ga-label')]  # extract the product url from the excess
                            # html
                            prodprice = pagelist[pagelist.index(line)+3][49:-7]
                            break
                    prodname = produrl[24:-1].replace("-", " ")
                    prod = {"prodname": prodname, "prodpricegbp": prodprice.replace(",", ""), "produrl": produrl}  # the
                    # format used for storing the products
                    if prod not in self.prodlist[brand]:
                        self.prodlist[brand].append(prod)  # put the product into the product list under each brand
                    pagelist = pagelist[pagelist.index('<divclass="bem-product-thumb--grid">')+15:]  # remove the product
                    # that has just been  processed
                x += 96
                g = requests.get(self.brandlist[brand], params={"g":str(x), "ps":"96"}, timeout=30)
                g.raise_for_status()
                f = g.text
                pagestr = str(f)
                pagestr = pagestr.replace(" ", "")
                pagelist = pagestr.split('\r\n')  # splits the page into a list rather than one long string, making some
                # methods easier later on
                pagelist = pagelist[pagelist.index('<divid="product-list">'):
                pagelist.index('<divclass="bem-footer"data-page-area="Footer">')]  # slice the list to remove unnecessary
                # content, from one of the top elements to one just underneath the products
            print("Finished brand:", brand)
        print("Finished downloading products")

    def dumpjson(self, dumpee, filename):
        print("Saving to ", filename)
        f = open(filename, "w")
        json.dump(dumpee, f)  # dump the dict into a json file
        f.close()
        print("Finished saving")

    def main(self):
        starttime = time.time()  # finding the start time to record total time taken for the program to execute
        self.findbrands("http://www.wiggle.co.uk/sitemap")
        self.findproducts("http://www.wiggle.co.uk/")
        self.dumpjson(self.prodlist, join("..", "json", "wiggleprodlist.json"))
        self.dumpjson(self.brandlist, join("..", "json", "wigglebrandlist.json"))

        fintime = time.time()  # finding the final time after code execution
        timetaken = round(fintime-starttime)
        print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
        # efficiency

if __name__ == "__main__":
    wpd = pd()
    wpd.main()