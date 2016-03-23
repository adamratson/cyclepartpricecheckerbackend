import json
import time
from urllib.request import urlopen
from os.path import join


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
                if "zoot" in brand:
                    prodlist["zoot"] = []  # add the brand key to the product list
                else:
                    brand = brand[33:brand.find('">')-1]  # remove the "/" from the brand name
                    prodlist[brand] = []  # add the brand key to the product list
        print("Brand list done!")
        return prodlist

    def findproducts(prodlist, url, getargs=""):
        for brand in prodlist:
            print("Downloading brand:", brand)
            x = 1
            g = urlopen(url+brand+getargs+"&g="+str(x))  # opens the brand page for each brand
            f = g.read()
            g.close()
            pagestr = str(f)
            pagestr = pagestr.replace(" ", "")
            pagelist = pagestr.split('\\r\\n')  # splits the page into a list rather than one long string, making some
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
                    if prod not in prodlist[brand]:
                        prodlist[brand].append(prod)  # put the product into the product list under each brand
                    pagelist = pagelist[pagelist.index('<divclass="bem-product-thumb--grid">')+15:]  # remove the product
                    # that has just been  processed
                x += 96
                g = urlopen(url+brand+getargs+"&g="+str(x))  # opens the brand page for each brand
                f = g.read()
                g.close()
                pagestr = str(f)
                pagestr = pagestr.replace(" ", "")
                pagelist = pagestr.split('\\r\\n')  # splits the page into a list rather than one long string, making some
                # methods easier later on
                pagelist = pagelist[pagelist.index('<divid="product-list">'):
                pagelist.index('<divclass="bem-footer"data-page-area="Footer">')]  # slice the list to remove unnecessary
                # content, from one of the top elements to one just underneath the products
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
                             "http://www.wiggle.co.uk/", "?ps=96")
    dumpjson(prodlist, join("..", "json", "wiggleprodlist.json"))

    fintime = time.time()  # finding the final time after code execution
    timetaken = round(fintime-starttime)
    print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
    # efficiency

if __name__ == "__main__":
    main()
#628kb
#1197kb
#1535kb