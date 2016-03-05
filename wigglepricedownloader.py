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
        firstbrand = "/1000-mile"
        lastbrand = "/zoot"
        tempbrands = f[f.find(firstbrand)-1:f.find(lastbrand)+5]
        tempbrands = tempbrands.split('<li>')  # split the string into the separate brands using '"'
        for brand in tempbrands:
            if "http://www.wiggle.co.uk/" in brand:  # is used to identify the brands as they are links to the page
                brand = brand[33:brand.find('">')-1]  # remove the "/" from the brand name
                prodlist[brand] = []  # add the brand key to the product list

        print("Brand list done!")
        print(prodlist)
        return prodlist

    def findproducts(prodlist, url):
        for brand in prodlist:
            print("Downloading brand:", brand)
            g = urlopen(url+brand)  # opens the brand page for each brand
            f = g.read()
            g.close()
            pagestr = str(f)
            pagelist = pagestr.split('\\n')  # splits the page into a list rather than one long string, making some
            # methods
            # easier later on
            pagelist = pagelist[pagelist.index(
                '<div id="search-results" class="bem-product-list--grid" data-page-area="Results">'):
            pagelist.index('<div class="bem-footer-notes">')]  # slice the list to remove unnecessary content,
            # from one of the top elements to one just underneath the products
            while pagelist.count('<div class="bem-sales-strip--grid">') > 1:  # check there are still unprocessed
                # products in the page
                descloc = pagelist.index('<div class="bem-sales-strip--grid">')+1
                produrl = pagelist[descloc]
                produrl = produrl[48:produrl.find('" data-ga-label')]  # extract the product url from the excess html
                prodname = produrl[1:-1]  # extract the product name from the url
                x = 0
                while x < 30:  # iterate through the lines until the product price is found
                    prodprice = pagelist[descloc+x]
                    if 'fromamt' in prodprice:  # this is the class of the div that held the price
                        prodprice = pagelist[descloc+x+1]
                        if prodprice == "<span class=\"bold\">":  # if the line that was meant to hold the price held
                            # this value, the price would actually be on the next line. This was due to some products
                            # not having reviews causing the html around it to change
                            prodprice = pagelist[descloc+x+2]
                        if prodprice == "<div class=\"colors\">":  # if the line that was meant to hold the price held
                            # this value, the product was unavailable and not able to be purchased. I still included it
                            # in the product list as it may become available again at some point
                            prodprice = "-"
                        break  # break the loop when the price has been found
                    x += 1
                prodprice = prodprice.replace('\\xc2\\xa3', "")  # this removed some of the excess html surrounding the
                # actual price

                #  whilst prodprice may not be defined, this can prove
                # useful as an error is raised if it fails to find the price. the price is needed for the product so
                # this is actually a useful feature
                prodprice = prodprice.replace('</li>', "")
                prodprice = prodprice.replace('</span>', "")  # these two lines removed more excess html
                prod = {"prodname": prodname, "prodpricegbp": prodprice, "produrl": produrl}  # the format used for
                # storing the products
                if prod not in prodlist[brand]:
                    prodlist[brand].append(prod)  # put the product into the product list under each brand
                pagelist = pagelist[pagelist.index('<li class="description">')+15:]  # remove the product that has just
                # been  processed
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
    prodlist = findproducts(findbrands("http://www.wiggle.co.uk/sitemap"),
                             "http://www.wiggle.co.uk/")
    dumpjson(prodlist, "wiggleprodlist.json")

    fintime = time.time()  # finding the final time after code execution
    timetaken = round(fintime-starttime)
    print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
    # efficiency

if __name__ == "__main__":
    main()
