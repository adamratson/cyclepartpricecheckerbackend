import time
import requests
from bs4 import BeautifulSoup
from re import sub


class WPD:
    def __init__(self):
        self.prodlist = {}
        self.brandlist = {}

    def findbrands(self, url):
        f = BeautifulSoup(requests.get(url).text, "lxml")  # opening the site map page

        print("Downloading brand list")

        brandlist = f.find("div", class_="bem-well").find_all('a')

        newbrandlist = {}

        for brand in brandlist:
            newbrandlist[brand.get_text()] = brand['href']
            self.prodlist[brand.get_text()] = []

        self.brandlist = newbrandlist

        print("Brand list done!")

    def findproducts(self):
        y = 1
        brandnum = len(self.brandlist)
        for brand in self.brandlist:
            print('\r'+"Downloading brand "+str(y)+" of "+str(brandnum), end="")
            x = 1
            g = BeautifulSoup(requests.get(self.brandlist[brand], params={"g": str(x), "ps": "96", "curr": "GBP"},
                                           timeout=30).text, "lxml")

            prods = g.find("div", class_="MainColumn").find_all("a")
            for tempprod in prods:
                if 'title' in tempprod.attrs.keys():
                    prodname = tempprod['title']
                    produrl = tempprod['href']
                    prodprice = tempprod.find_next("span", class_="bem-product-price__unit--grid").get_text()
                    prod = {"prodname": prodname, "prodpricegbp": prodprice[1:], "produrl": produrl}
                    self.prodlist[brand].append(prod)
            while True:
                x += 96

                if "Sorry, we couldn't find anything that matches your search." not in requests.get(
                        self.brandlist[brand], params={"g": str(x), "ps": "96", "curr": "GBP"}).text:
                    g = BeautifulSoup(requests.get(self.brandlist[brand], params={"g": str(x), "ps": "96",
                                                                                  "curr": "GBP"}).text, "lxml")

                    prods = g.find("div", class_="MainColumn").find_all("a")
                    for tempprod in prods:
                        if 'title' in tempprod.attrs.keys():
                            prodname = tempprod['title']
                            produrl = tempprod['href']
                            prodprice = tempprod.find_next("span", class_="bem-product-price__unit--grid").get_text()

                            prod = {"prodname": prodname, "prodpricegbp": prodprice[1:], "produrl": produrl}
                            self.prodlist[brand].append(prod)
                else:
                    break
            y += 1
        print('')
        print("Finished downloading products")

    def main(self):
        starttime = time.time()  # finding the start time to record total time taken for the program to execute
        self.findbrands("http://www.wiggle.co.uk/sitemap")
        self.findproducts()
        fintime = time.time()  # finding the final time after code execution
        timetaken = round(fintime - starttime)
        print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for
        # enhancing efficiency
        return self.prodlist


class CRCPD:
    def __init__(self):
        self.prodlist = {}
        self.brandlist = {}
        self.cookies = {"countryCode": "GB", "currencyCode": "GBP", "languageCode": "en"}

    def findbrands(self, url):
        f = BeautifulSoup(requests.get(url, cookies=self.cookies).text, "lxml")

        print("Downloading brand list")
        brandlist = f.find("ul", id="AllbrandList").find_all('a')

        newbrandlist = {}

        for brand in brandlist:
            newbrandlist[brand.get_text()] = "http://chainreactioncycles.com" + brand['href']
            self.prodlist[brand.get_text()] = []

        self.brandlist = newbrandlist

        print("Brand list done!")

    def findproducts(self, url):
        brandnum = len(self.brandlist)
        y = 1
        for brand in self.brandlist:
            print('\r'+"Downloading brand "+str(y)+" of "+str(brandnum), end="")

            g = requests.get(self.brandlist[brand], params={"perPage": "20000"}, cookies=self.cookies, timeout=60)

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
                                prodprice = prodprice[prodprice.find('<span class="bold">') + 20:
                                prodprice.find('</span>')]

                            prod = {"prodname": prodname, "prodpricegbp": prodprice, "produrl": url + produrl}
                            self.prodlist[brand].append(prod)
                y += 1
        print("Finished downloading products")

    def main(self):
        starttime = time.time()  # finding the start time to record total time taken for the program to execute
        self.findbrands("http://www.chainreactioncycles.com/sitemap")
        self.findproducts("http://www.chainreactioncycles.com/gb/en")
        fintime = time.time()  # finding the final time after code execution
        timetaken = round(fintime - starttime)
        print(timetaken, "seconds")  # prints the time taken for the program to complete in seconds, useful for
        # enhancing efficiency
        return self.prodlist


class BDPD:
    def __init__(self):
        self.prodlist = {}
        self.brandlist = {}

    def findbrands(self, url):
        g = requests.get(url).text  # opening the site map page

        print("Downloading brand list")
        firstbrand = "100-percent"
        lastbrand = "zwoelfender-1411"
        tempbrands = f[f.find(firstbrand):f.find(lastbrand) + len(lastbrand)]
        tempbrands = tempbrands.split('<a')  # split the string into the separate brands using '"'
        for brand in tempbrands:
            if "/en/" in brand:  # is used to identify the brands as they are links to the page
                if lastbrand in brand:
                    self.prodlist[lastbrand] = []  # add the brand key to the product list
                else:
                    if "/shop/" in brand:
                        brandurl = "http://bike-discount.de" + brand[7:brand.find("title") - 2]
                        brand = brand[brand.find('title="') + 7:brand.find(">") - 1]
                    else:
                        brandurl = "http://bike-discount.de" + brand[7:brand.find("title") - 2]
                        brand = brand[brand.find('title="') + 7:brand.find(">") - 1]
                    self.brandlist[brand] = brandurl
                    self.prodlist[brand] = []  # add the brand key to the product list
        print("Brand list done!")

    def findproducts(self):
        for brand in self.brandlist:
            print("Downloading brand:", brand)
            f = BeautifulSoup(requests.get(self.brandlist[brand] + "/l-24", timeout=60).gettext, "lxml")

            """
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
            """
            print("Finished brand:", brand)
        print("Finished downloading products")

    def cleanbikediscount(self):
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
        self.findproducts()
        self.cleanbikediscount()
        fintime = time.time()  # finding the final time after code execution
        timetaken = round(fintime - starttime)
        print(timetaken,
              "seconds")  # prints the time taken for the program to complete in seconds, useful for enhancing
        # efficiency
        return self.prodlist


if __name__ == "__main__":
    mycrcpd = CRCPD()
    mycrcpd.main()
    mywpd = WPD()
    mywpd.main()
    mybdpd = BDPD()
    mybdpd.main()
