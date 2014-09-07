#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, sys
import lxml.html as html
from time import sleep

seloger_url = "http://www.seloger.com/annuaire/agences/pro-paris-75/?idtypeprofessionnel=1&idtt=1&tri=nom_a&LIST-AGENCIESpg=177"

cururl = seloger_url
while cururl:
    doc = html.fromstring(urllib.urlopen(cururl).read().decode("utf8"))

    annonces = doc.find_class("listing")
    for annonce in annonces:

        title = annonce.xpath("div/h2")[0].text_content().encode("utf-8").strip("\n\t \r")
        adress = annonce.xpath("div/p[@class='adress']")[0].text_content().encode("utf-8").strip("\n\t\r ").replace("\r\n", " ")
        try:
            tel = annonce.xpath("div/button[@class='agency_phone']/@data-phone")[0]
        except:
            tel = ""
        try:
            adress, cp = adress.split(' 750')
            cp = "750%s" % cp[:2]
        except Exception as e:
            try:
                adress, cp = adress.split(' 751')
                cp = "750%s" % cp[:2]
            except Exception as e:
                print >> sys.stderr, type(e), e, title, adress, tel
                continue
        print >> sys.stdout, '%s\t%s\t%s\t%s' % (title, adress, cp, tel)

    nexturl = doc.find_class("pagination_next")
    if nexturl and nexturl[0].xpath("@href"):
        cururl = nexturl[0].xpath("@href")[0]
    else:
        cururl = ""

    sleep(2)
