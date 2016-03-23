import json
import time
from urllib.request import urlopen
from os.path import join
from re import sub
from urllib import error


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
                    prodlist[lastbrand] = []  # add the brand key to the product list
                else:
                    brand = brand[16:brand.find("title")-2]  # remove the "/" from the brand name
                    prodlist[brand] = []  # add the brand key to the product list
        print("Brand list done!")
        return prodlist

    def findproducts(prodlist, url):
        for brand in prodlist:
            print("Downloading brand:", brand)
            try:
                g = urlopen(url+brand, timeout=60)  # opens the brand page for each brand
            except error.URLError:
                g = urlopen(url+brand, timeout=60)  # opens the brand page for each brand
            f = g.read()
            g.close()
            pagestr = str(f)
            pagestr = pagestr.replace("\\n", "")
            pagelist = pagestr.split('>')  # splits the page into a list rather than one long string, making some
            # methods easier later on
            pagelist = pagelist[pagelist.index('<img src="/media/k23230/k78/87927_logo_bikediscount_head.png" width="300" height="46" alt="Bike-Discount" id="logo"'):
            pagelist.index('<footer id="layout_footer" class="layout_footer_standard uk-clear"')]  # slice the
            # list to remove unnecessary content, from one of the top elements to one just underneath the products
            while pagelist.count('<div class="uk-width-1-2 uk-width-medium-1-3"') > 1:  # check there are still
                # unprocessed products in the page
                for line in pagelist:
                    if '<div class="uk-width-1-2 uk-width-medium-1-3"' in line:
                        produrltemp = pagelist[pagelist.index(line)+6]
                        produrl = produrltemp[10:produrltemp.find('title="')-2]  # extract the product url
                        # from the excess html
                        prodprice = pagelist[pagelist.index('<div class="price has-price-text"')+2][:-13]
                prodname = produrl[7:produrl.find("wg_id-")-1].replace("-", " ")
                prod = {"prodname": prodname, "prodpriceeur": prodprice, "produrl": url+produrl}  # the format used for
                # storing the products
                if prod not in prodlist[brand]:
                    prodlist[brand].append(prod)  # put the product into the product list under each brand
                pagelist = pagelist[pagelist.index('<div class="uk-width-1-2 uk-width-medium-1-3"')+15:]  # remove the
                # product that has just been processed
            print("Finished brand:", brand)
        print("Finished downloading products")
        return prodlist

    def dumpjson(dumpee, filename):
        print("Saving to ", filename)
        f = open(filename, "w")
        json.dump(dumpee, f)  # dump the dict into a json file
        f.close()
        print("Finished saving")

    def cleanBikeDiscount(prodlist):
        newprodlist = {}
        for key, value in prodlist.items():
            brand = key.replace("-", " ")
            brand = sub(r"\d", "", brand)
            if brand[:-1] == " ":
                brand = brand[:-1]
            newprodlist[brand] = value
        return newprodlist

    starttime = time.time()  # finding the start time to record total time taken for the program to execute
    prodlist = findproducts(findbrands("http://www.bike-discount.de/en/brands"), "http://www.bike-discount.de/en/shop/")
    prodlist = cleanBikeDiscount(prodlist)
    print(prodlist)
    dumpjson(prodlist, join("..", "json", "bikediscountprodlist.json"))

    fintime = time.time()  # finding the final time after code execution
    timetaken = round(fintime-starttime)
    print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
    # efficiency

if __name__ == "__main__":
    main()
