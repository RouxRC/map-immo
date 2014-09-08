#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, sys
import lxml.html as html
from time import sleep
from geocode import GeoCoder

seloger_url = "http://www.seloger.com/annuaire/agences/pro-paris-75/?idtypeprofessionnel=1&idtt=1&tri=nom_a"

G = GeoCoder(75, verbose=True)

n0 = 0
n1 = 0
cururl = seloger_url
print >> sys.stdout, "Nom,Adresse,Code Postal,Téléphone,lat,lon"
while cururl:
    doc = html.fromstring(urllib.urlopen(cururl).read().decode("utf8"))

    annonces = doc.find_class("listing")
    for annonce in annonces:
        n0 += 1

        title = annonce.xpath("div/h2")[0].text_content().encode("utf-8").strip("\n\t \r")
        adress = annonce.xpath("div/p[@class='adress']")[0].text_content().encode("utf-8").strip("\n\t\r ").replace("\r\n", " ")
        adress = adress.replace("avenue montagne", "avenue montaigne")
        try:
            tel = annonce.xpath("div/button[@class='agency_phone']/@data-phone")[0]
        except:
            tel = ""
        try:
            lat, lon = G.geocode(adress)
            print >> sys.stdout, '%s\t%s\t%s\t%s\t%s' % (title, adress, tel, lat, lon)
            n1 += 1
        except TypeError:
            pass
            print >> sys.stderr, "[WARNING] NO GPS found for adress", title, ":", adress

    nexturl = doc.find_class("pagination_next")
    if nexturl and nexturl[0].xpath("@href"):
        cururl = nexturl[0].xpath("@href")[0]
        sleep(2)
    else:
        cururl = ""

print >> sys.stderr, "[INFO] Found %s agences and %s geolocalized (%s)" % (n0, n1, str(100*n1/n0)+"%")
