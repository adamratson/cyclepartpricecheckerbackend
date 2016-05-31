import time
import requests
from bs4 import BeautifulSoup
from re import sub


class wpd():
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

    def main(self):
        starttime = time.time()  # finding the start time to record total time taken for the program to execute
        self.findbrands("http://www.wiggle.co.uk/sitemap")
        self.findproducts("http://www.wiggle.co.uk/")
        fintime = time.time()  # finding the final time after code execution
        timetaken = round(fintime-starttime)
        print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
        # efficiency
        return self.prodlist


class crcpd:
    def __init__(self):
        self.prodlist = {}
        self.brandlist = {}
        self.cookies = {"countryCode":"GB", "currencyCode":"GBP", "languageCode":"en"}

    def findbrands(self, url):
        g = requests.get(url, cookies=self.cookies)
        f = g.text
        f = BeautifulSoup(f, "lxml")

        print("Downloading brand list")
        brandlist = f.find("ul", id="AllbrandList").find_all('a')

        newbrandlist = {}

        for brand in brandlist:
            newbrandlist[brand.get_text()] = "http://chainreactioncycles.com"+brand['href']
            self.prodlist[brand.get_text()] = []

        self.brandlist = newbrandlist

        print("Brand list done!")

    def findproducts(self, url):
        for brand in self.brandlist:
            print("Downlding brand:", brand)

            try:
                g = requests.get(self.brandlist[brand], params={"perPage":"20000"}, cookies=self.cookies, timeout=60)
            except requests.exceptions.ConnectionError:
                g = requests.get(self.brandlist[brand], params={"perPage":"20000"}, cookies=self.cookies, timeout=60)

            if "No items match your search for" not in g:
                parsed_html = BeautifulSoup(g.text, "lxml")
                containerlist = parsed_html.find_all('div', class_='products_details_container')

                if containerlist is not None:
                    for container in containerlist:
                        produrl = container.find('a')['href']
                        prodname = container.find('a').find('img')['alt']
                        pricetag = container.find('li', class_='fromamt')
                        if pricetag is None:
                            break
                        else:
                            prodprice = str(pricetag.contents)[4:-2]

                            if '<span class="bold">' in prodprice:
                                prodprice = prodprice[prodprice.find('<span class="bold">')+20:prodprice.find('</span>')]

                            prod = {"prodname": prodname, "prodpricegbp": prodprice, "produrl": url+produrl}
                            self.prodlist[brand].append(prod)
                print("Finished brand:", brand)
        print("Finished downloading products")

    def main(self):
        starttime = time.time()  # finding the start time to record total time taken for the program to execute
        self.findbrands("http://www.chainreactioncycles.com/sitemap")
        self.findproducts("http://www.chainreactioncycles.com/gb/en")
        fintime = time.time()  # finding the final time after code execution
        timetaken = round(fintime-starttime)
        print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
        # efficiency
        return self.prodlist


class bdpd():
    def __init__(self):
        self.prodlist = {}
        self.brandlist = {}

    def findbrands(self, url):
        g = urlopen(url)  # opening the site map page
        f = g.read()  # using the read function to extract the contents of the html request
        g.close()  # close the file to save memory and prevent a memory leak

        f = str(f)  # .read() returns a binary value, this converts it to a string
        print("Downloading brand list")
        firstbrand = "100-percent"
        lastbrand = "zwoelfender-1411"
        tempbrands = f[f.find(firstbrand):f.find(lastbrand)+len(lastbrand)]
        tempbrands = tempbrands.split('<a')  # split the string into the separate brands using '"'
        for brand in tempbrands:
            if "/en/" in brand:  # is used to identify the brands as they are links to the page
                if lastbrand in brand:
                    self.prodlist[lastbrand] = []  # add the brand key to the product list
                else:
                    if "/shop/" in brand:
                        brandurl = "http://bike-discount.de"+brand[7:brand.find("title")-2]
                        brand = brand[brand.find('title="')+7:brand.find(">")-1]
                    else:
                        brandurl = "http://bike-discount.de"+brand[7:brand.find("title")-2]
                        brand = brand[brand.find('title="')+7:brand.find(">")-1]
                    self.brandlist[brand] = brandurl
                    self.prodlist[brand] = []  # add the brand key to the product list
        print("Brand list done!")

    def findproducts(self, url):
        for brand in self.brandlist:
            print("Downloading brand:", brand)
            try:
                g = urlopen(self.brandlist[brand]+"/l-24", timeout=60)  # opens the brand page for each brand
            except error.URLError:
                g = urlopen(self.brandlist[brand]+"/l-24", timeout=60)  # opens the brand page for each brand
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
                if prod not in self.prodlist[brand]:
                    self.prodlist[brand].append(prod)  # put the product into the product list under each brand
                pagelist = pagelist[pagelist.index('<div class="uk-width-1-2 uk-width-medium-1-3"')+15:]  # remove the
                # product that has just been processed
            print("Finished brand:", brand)
        print("Finished downloading products")

    def cleanBikeDiscount(self):
        newprodlist = {}
        for key, value in self.prodlist.items():
            brand = key.replace("-", " ")
            brand = sub(r"\d", "", brand)
            if brand[:-1] == " ":
                brand = brand[:-1]
            newprodlist[brand] = value
        self.prodlist = newprodlist

    def main(self):
        starttime = time.time()  # finding the start time to record total time taken for the program to execute
        self.findbrands("http://www.bike-discount.de/en/brands")
        self.findproducts("http://www.bike-discount.de/")
        self.cleanBikeDiscount()
        fintime = time.time()  # finding the final time after code execution
        timetaken = round(fintime-starttime)
        print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
        # efficiency
        return self.prodlist

if __name__ == "__main__":
    mycrcpd = crcpdler()
    mycrcpd.main()
    mywpd = wpd()
    mywpd.main()
    mybdpd = bdpd()
    mybdpd.main()

