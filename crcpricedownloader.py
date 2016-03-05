from urllib.request import urlopen
import json
import time


def main():
    starttime = time.time()
    g = urlopen("http://www.chainreactioncycles.com/sitemap")
    f = g.read()
    g.close()
    crcprodlist = {}

    f = str(f)
    print("Downloading brand list")
    tempbrands = f[f.find("/100-")-1:f.find("/zoot")+5].replace('</a></li>\\n<li><a href=', "")
    tempbrands = tempbrands.replace(">", "")
    tempbrands = tempbrands.split('"')
    for brand in tempbrands:
        if "/" in brand:
            brand = brand[1:]
            crcprodlist[brand] = []
    print("Brand list done!")
    # before the change to .read()
    """
    brands = False
    for line in f:
        line = str(line)

        blacklisted = False
        whitelist = ['href']
        blacklist = ['onclick', 'customer-service', 'hub', 'dns-prefetch', 'stylesheet', 'alternate', 'script']
        for whiteword in whitelist:
            if whiteword in str(line):
                for blackword in blacklist:
                    if blackword in str(line):
                        blacklisted = True
                if not blacklisted:
                    print(line)

        firstbrand = '/100-'
        lastbrand = '/zoot'

        if firstbrand in g:
            brands = True
        if lastbrand in g:
            brands = False
            brandlist.append(lastbrand)
            break
        if brands:
            if '<a href=\"' in line and '</a>' in line:
                brand = line[line.index('<a href=\"'):line.index('</a>')]
                brand = brand[brand.find('"'):brand.replace('"', 'XXX', 1).find('"')]
                brand = brand.replace('>', "")
                brand = brand.replace('"', "")
                brandlist.append(brand)
"""

    for brand in crcprodlist:
        print("Downloading brand:", brand)
        g = urlopen("http://www.chainreactioncycles.com/"+brand)
        f = g.read()
        g.close()
        pagestr = str(f)
        pagelist = pagestr.split('\\n')
        pagelist = pagelist[pagelist.index('<div class="product_grid_view pdctcontr" id="grid-view">'):
                    pagelist.index('<div class="toolbarBottom">')]
        x = 1
        while pagelist.count('<li class="description">') > 1:
            descloc = pagelist.index('<li class="description">')+1
            produrl = pagelist[descloc]
            produrl = produrl[9:produrl.find('" onclick')]
            prodname = produrl[1:produrl.index("/rp-prod")]
            x=0
            while x < 30:
                prodprice = pagelist[descloc+x]
                if 'fromamt' in prodprice:
                    prodprice = pagelist[descloc+x+1]
                    if prodprice == "<span class=\"bold\">":
                        prodprice = pagelist[descloc+x+2]
                    if prodprice == "<div class=\"colors\">":
                        prodprice = "-"
                    break
                x += 1
            prodprice = prodprice.replace('\\xc2\\xa3', "")
            prodprice = prodprice.replace('</li>', "")
            prodprice = prodprice.replace('</span>', "")
            prod = {"prodname":prodname, "prodpricegbp":prodprice, "produrl":produrl}
            if prod not in crcprodlist[brand]:
                crcprodlist[brand].append(prod)
            pagelist = pagelist[pagelist.index('<li class="description">')+15:]
        print("Finished brand:", brand)
    print("Finished downloading products")

    print("Saving to prodlist.json")
    f = open("crcprodlist.json", "w")
    json.dump(crcprodlist, f)
    f.close()
    print("Finished saving")


    """
    for line in f:
        line = str(line)
        if "rp-prod" in line:
            blacklist = ['customer-service', 'hub', 'dns-prefetch', 'stylesheet', 'alternate']
            for blackword in blacklist:
                if blackword not in line:
                    prod = line[line.find("<a href="):line.find("onclick=")]
                    prod = prod.replace("<a href=", "")
                    prodid = prod[-8:]
                    prodid = prodid.replace(" ", "")
                    prod = prod[:prod.replace('/', 'XXX', 1).find('/')]
                    prod = prod[:-2]
                    prod = prod.replace('"', "")
                    prodid = prodid.replace('"', "")
                    prodid = sub(r"\D", "", prodid)
                    if prodid not in prodlist and prodid != '':
                        prodlist[prodid] = prod
                        """
    fintime = time.time()
    timetaken = round(fintime-starttime)
    print(timetaken, "seconds")

if __name__ == "__main__":
    main()
