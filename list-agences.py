#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, sys
import lxml.html as html
from time import sleep
from geocode import GeoCoder

seloger_url = "http://www.seloger.com/annuaire/agences/pro-paris-75/?idtypeprofessionnel=1&idtt=1&tri=nom_a"

G = GeoCoder(75)

n0 = 0
n1 = 0
cururl = seloger_url
print >> sys.stdout, "Nom,Adresse,Téléphone,Code Postal,lat,lon"
while cururl:
    doc = html.fromstring(urllib.urlopen(cururl).read().decode("utf8"))

    annonces = doc.find_class("listing")
    for annonce in annonces:
        n0 += 1
        title = annonce.xpath("div/h2")[0].text_content().encode("utf-8").strip("\n\t \r")

        adress = annonce.xpath("div/p[@class='adress']")[0].text_content().encode("utf-8").strip("\n\t\r ").replace("\r\n", " ")
        adress = adress.replace("avenue montagne", "avenue montaigne")
        adress = adress.replace("poissoniere", "poissonniere")
        adress = adress.replace("le peltier", "le peletier")
        adress = adress.replace("de wagran", "de wagram")
        adress = adress.replace("lazarre", "lazare")
        adress = adress.replace("vielle", "vieille")
        adress = adress.replace("toqueville", "tocqueville")
        adress = adress.replace("hausmann", "haussmann")
        adress = adress.replace("malsherbes", "malesherbes")
        adress = adress.replace("cinqs ", "cinq ")
        adress = adress.replace("george mandel", "georges mandel")
        adress = adress.replace("défence", "defense")
        adress = adress.replace("gauthier", "gautier")
        adress = adress.replace("croulbarbe", "croulebarbe")
        adress = adress.replace("grenetta", "greneta")
        adress = adress.replace("general le clerc", "general leclerc")
        adress = adress.replace("bobiillot", "bobillot")
        adress = adress.replace("ponthieux", "ponthieu")
        adress = adress.replace("poularch", "poulmarch")
        adress = adress.replace("landrouzy", "landouzy")
        adress = adress.replace("danremon", "damremon")
        adress = adress.replace("voltaire26 rue de malte", "voltaire")
        adress = adress.replace("rambervilliers", "rambervillers")
        adress = adress.replace("jaures le belvedere", "jaures")
        adress = adress.replace("d. roosevelt", "delano roosevelt")
        adress = adress.replace("h. barbus", "henri barbus")
        adress = adress.replace("dela paix", "de la paix")
        adress = adress.replace("froy dabbans", "froy d'abbans")

        try:
            tel = annonce.xpath("div/button[@class='agency_phone']/@data-phone")[0]
        except:
            tel = ""

        try:
            cp, lat, lon = G.geocode(adress, return_postcode=True)
            print >> sys.stdout, '%s\t%s\t%s\t%s\t%s\t%s' % (title, adress, tel, cp, lat, lon)
            n1 += 1
        except TypeError:
            print >> sys.stdout, '%s\t%s\t%s\t\t\t' % (title, adress, tel)
            print >> sys.stderr, "[WARNING] NO GPS found for agence", title, ":", adress

    nexturl = doc.find_class("pagination_next")
    if nexturl and nexturl[0].xpath("@href"):
        cururl = nexturl[0].xpath("@href")[0]
        sleep(2)
    else:
        cururl = ""

print >> sys.stderr, "[INFO] Found %s agences and %s geolocalized (%s)" % (n0, n1, str(100*n1/n0)+"%")
