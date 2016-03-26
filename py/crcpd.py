import json
import time
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
        tempbrands = f[f.find("/100-")-15:f.find("/zoot")+11]
        tempbrands = tempbrands.split('</li>')
        for brand in tempbrands:
            if '<a href="' in brand:
                brand = brand.replace(">", "YYY", 1)
                brandname = brand[brand.find(">")+1:brand.find("</a>")]
                brandurl = brand[17:brand.find(">")-1]
                self.brandlist[brandname] = "http://chainreactioncycles.com"+brandurl
                self.prodlist[brandname] = []
        print("Brand list done!")

    def findproducts(self, url):
        for brand in self.brandlist:
            print("Downloading brand:", brand)
            g = urlopen(self.brandlist[brand]+"?perPage=20000")  # opens the brand page for each brand
            f = g.read()
            g.close()
            pagestr = str(f)
            if "No items match your search for" not in pagestr:
                pagelist = pagestr.split('\\n')  # splits the page into a list rather than one long string, making some
                # methods easier later on
                pagelist = pagelist[pagelist.index('<div class="product_grid_view pdctcontr" id="grid-view">'):
                pagelist.index('<div class="toolbarBottom">')]  # slice the list to remove unnecessary content, from one
                #  of the top elements to one just underneath the products
                while pagelist.count('<li class="description">') > 1:  # check there are still unprocessed products in
                    # the page
                    descloc = pagelist.index('<li class="description">')+1
                    produrl = pagelist[descloc]
                    produrl = produrl[9:produrl.find('" onclick')]  # extract the product url from the excess html
                    prodname = produrl[1:produrl.index("/rp-prod")]  # extract the product name from the url
                    prodname = prodname.replace("-", " ")
                    if "bundle" not in prodname and "builder" not in prodname:
                        prodprice = pagelist[pagelist.index('<li class="fromamt">')+1]
                        if prodprice == '<span class="bold">':
                            prodprice = pagelist[pagelist.index('<li class="fromamt">')+2]
                        prodprice = prodprice.replace('\\xc2\\xa3', "")  # this removed some of the excess html surrounding
                        # the actual price
                        #  whilst prodprice may not be defined, this can prove
                        # useful as an error is raised if it fails to find the price. the price is needed for the product so
                        # this is actually a useful feature
                        prodprice = prodprice.replace('</li>', "")
                        prodprice = prodprice.replace('</span>', "")  # these two lines removed more excess html
                        if "&nbsp;" in prodprice:
                            prodprice = prodprice[prodprice.replace("&nbsp", "YYY", 1).find("&nbsp;")+6:]
                        try:
                            prodprice = float(prodprice)
                            prod = {"prodname": prodname, "prodpricegbp": prodprice, "produrl": url[:-1]+produrl}  # the format
                            # used for storing the products
                            if prod not in self.prodlist[brand]:
                                self.prodlist[brand].append(prod)  # put the product into the product list under each brand
                        except ValueError:
                            pass
                    pagelist = pagelist[pagelist.index('<li class="description">')+15:]  # remove the product that has
                    # just been  processed
                print("Finished brand:", brand)
        print("Finished downloading products")

    def dumpjson(self, dumpee, filename):
        print("Saving to prodlist.json")
        f = open(filename, "w")
        json.dump(dumpee, f)  # dump the dict into a json file
        f.close()
        print("Finished saving")

    def main(self):
        starttime = time.time()  # finding the start time to record total time taken for the program to execute
        self.findbrands("http://www.chainreactioncycles.com/sitemap")
        self.findproducts("http://www.chainreactioncycles.com")
        self.dumpjson(self.prodlist, join("..", "json", "crcprodlist.json"))
        self.dumpjson(self.brandlist, join("..", "json", "crcbrandlist.json"))
        fintime = time.time()  # finding the final time after code execution
        timetaken = round(fintime-starttime)
        print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
        # efficiency

if __name__ == "__main__":
    crcpd = pd()
    crcpd.main()
