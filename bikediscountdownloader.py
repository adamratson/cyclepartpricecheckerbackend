import json
import time
from urllib.request import urlopen


def main():
    def findbrands(url):
        g = urlopen(url)  # opening the site map page
        f = g.read()  # using the read function to extract the contents of the html request
        g.close()  # close the file to save memory and prevent a memory leak
        prodlist = {}

        f = str(f)  # .read() returns a binary value, this converts it to a string
        print("Downloading brand list")
        firstbrand = "100-percent"
        lastbrand = "zwoelfender-1411"
        tempbrands = f[f.find(firstbrand):f.find(lastbrand)+len(lastbrand)]
        tempbrands = tempbrands.split('<a')  # split the string into the separate brands using '"'
        for brand in tempbrands:
            if "/en/shop/" in brand:  # is used to identify the brands as they are links to the page
                if lastbrand in brand:
                    prodlist["en/shop/"+lastbrand] = []  # add the brand key to the product list
                else:
                    brand = brand[8:brand.find("title")-2]  # remove the "/" from the brand name
                    prodlist[brand] = []  # add the brand key to the product list

        print("Brand list done!")
        return prodlist

    def findproducts(prodlist, url):
        for brand in prodlist:
            print("Downloading brand:", brand)
            g = urlopen(url+brand)  # opens the brand page for each brand
            f = g.read()
            g.close()
            pagestr = str(f)
            pagestr = pagestr.replace("\\n", "")
            pagelist = pagestr.split('>')  # splits the page into a list rather than one long string, making some
            # methods easier later on
            pagelist = pagelist[:pagelist.index('<div class="layout-body-outer-wrapper page-footer"')]  # slice the
            # list to remove unnecessary content, from one of the top elements to one just underneath the products
            while pagelist.count('<div class="title-and-description"') > 1:  # check there are still unprocessed
                # products in the page
                for line in pagelist:
                    if '<h3 class="title"' in line:
                        produrltemp = pagelist[pagelist.index(line)+1]
                        produrl = produrltemp[8:produrltemp.find('title="')-2]  # extract the product url
                        # from the excess html
                        prodprice = pagelist[pagelist.index('<td class="block1"')+4][:-12]
                prodname = produrl[16:produrl.find("wg_id-")-1].replace("-", " ")
                prod = {"prodname": prodname, "prodpriceeur": prodprice, "produrl": produrl}  # the format used for
                # storing the products
                if prod not in prodlist[brand]:
                    prodlist[brand].append(prod)  # put the product into the product list under each brand
                pagelist = pagelist[pagelist.index('<div class="title-and-description"')+15:]  # remove the product
                # that has just been  processed
            print("Finished brand:", brand)
        print("Finished downloading products")
        return prodlist

    def dumpjson(dumpee, filename):
        print("Saving to ", filename)
        f = open(filename, "w")
        json.dump(dumpee, f)  # dump the dict into a json file
        f.close()
        print("Finished saving")

    starttime = time.time()  # finding the start time to record total time taken for the program to execute
    prodlist = findproducts(findbrands("http://www.bike-discount.de/en/brands"), "http://www.bike-discount.de/")
    dumpjson(prodlist, "bikediscountprodlist.json")

    fintime = time.time()  # finding the final time after code execution
    timetaken = round(fintime-starttime)
    print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
    # efficiency

if __name__ == "__main__":
    main()
