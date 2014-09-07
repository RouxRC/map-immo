#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, csv, re

with open("data/agences.csv") as f:
    agences = list(csv.reader(f, delimiter="\t"))[1:]

with open("data/bano-75.csv") as f:
    bano = list(csv.reader(f))[1:]

re_a = re.compile(r'[àâä]')
re_e = re.compile(r'[éèêë]')
re_i = re.compile(r'[îï]')
re_o = re.compile(r'[ôö]')
re_u = re.compile(r'[ùûü]')
re_all = re.compile(r'[^0-9a-z]')
re_bld = re.compile(r'(^| )bl?v?d ')
re_ave = re.compile(r'(^| )ave?\.? ')
re_fbg = re.compile(r'(^| )fb?g ')
re_deu = re.compile(r" d((e l)?[' ]|[eu]( la|s)? )")
re_st = re.compile(r"(^| )st ")
def clean_accents(s):
    s = s.lower().strip("\r\n\t ")
    s = re_deu.sub(" ", s)
    s = re_st.sub(" saint ", s)
    s = re_bld.sub(" boulevard ", s)
    s = re_ave.sub(" avenue ", s)
    s = re_fbg.sub(" faubourg ", s)
    s = s.replace(' dr ', " docteur ")
    if s.startswith("r "):
        s = s.replace('r ', "rue ", 1)
    if s.startswith("reu "):
        s = s.replace('reu ', "rue ", 1)
    s = s.replace('rdt point', "rond-point")
    s = re_a.sub("a", s)
    s = re_e.sub("e", s)
    s = re_i.sub("i", s)
    s = re_o.sub("o", s)
    s = re_u.sub("u", s)
    s = s.replace("ç", "c")
    return re_all.sub("", s)

adresses = {}
for line in bano:
    if line[3] not in adresses:
        adresses[line[3]] = {}
    line[2] = clean_accents(line[2])
    if line[2] not in adresses[line[3]]:
        adresses[line[3]][line[2]] = {}
    line[1] = line[1].lower()
    adresses[line[3]][line[2]][line[1]] = (line[6], line[7])

re_clean = re.compile(r"^\D*(\d+)([ -]+\d+)?( (bis|ter|qua)+ )?")
re_biss = re.compile(r"(\d)b[is]*")
re_digit = re.compile(r"\D")
digitize = lambda x: int(re_digit.sub("", x))

def find_number(cp, rue, chiffre):
    try:
        rueb = adresses[cp][rue]
    except:
        raise KeyError
    if chiffre in rueb:
        return rueb[chiffre]
    chiffre = digitize(chiffre)
    digits = [(k, digitize(k)) for k in rueb.keys()]
    impair = chiffre % 2
    dig_impa = [(abs(d2-chiffre), d) for d,d2 in digits if d2 % 2]
    dig_pair = [(abs(d2-chiffre), d) for d,d2 in digits if not (d2 % 2)]

    if impair:
        if dig_impa:
            _,key = min(dig_impa)
        else:
            _,key = min(dig_pair)
    else:
        if dig_pair:
            _,key = min(dig_pair)
        else:
            _,key = min(dig_impa)
    print key
    return rueb[key]


print "Nom,Adresse,Code Postal,Téléphone,lat,lon"
for agence in agences:
    try:
        cp = agence[2].replace("75116", "75016")
        adr = re_biss.sub(r"\1b ", agence[1]).lower()
        adr = re_clean.sub(lambda x: x.group(1) + (x.group(4)[:1]+" " if x.group(4) else ""), adr)
        chiffre, rue = adr.split(" ", 1)
        rue = clean_accents(rue)
        agence += find_number(cp, rue, chiffre)
        print ",".join(agence)
    except KeyError:
        print >> sys.stderr, "NO GPS found for adress", agence, chiffre, "/", rue
