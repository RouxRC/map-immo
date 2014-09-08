#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, re, requests
if not os.path.exists(".cache"):
    os.makedirs(".cache")

class GeoCoder(object):

    def __init__(self, dept=None, verbose=False):
        self.verbose = verbose
        self.set_departement(dept)

    def set_departement(self, dept):
        self.adresses = {}
        self.loaded = []
        if dept:
            self._load_departement(dept)

    def _load_departement(self, dept):
        dept = str(dept).upper()
        if len(dept) == 1:
            dept = "0%s" %dept

      # Download bano data if not already in cache
        banofile = os.path.join(".cache", "bano-%s.csv" % dept)
        if not os.path.exists(banofile):
            try:
                with open(banofile, "w") as f:
                    if self.verbose:
                        sys.stderr.write("[INFO] Downloading bano data for dept %s\n" % dept)
                    f.write(requests.get("https://raw.githubusercontent.com/osm-fr/bano-data/master/bano-%s.csv" % dept).text.encode("utf-8"))
            except:
                raise(Exception("[ERROR] Couldn't download bano data for dept %s" % dept))

      # Load bano data
        try:
            with open(banofile) as f:
                data = f.read().decode('utf-8')
        except:
            raise(Exception("[ERROR] Couldn't load bano data for dept %s in %s" % (dept, banofile)))

      # Build tree of postcodes/streets/numbers
        for line in data.split("\n"):
            if not line:
                continue
            line = line.split(",")
            if line[3] not in self.adresses:
                self.adresses[line[3]] = {}
            line[2] = hash_adress(line[2])
            if line[2] not in self.adresses[line[3]]:
                self.adresses[line[3]][line[2]] = {}
            line[1] = clear_blanks(line[1])
            self.adresses[line[3]][line[2]][line[1]] = (float(line[6]), float(line[7]))
        if dept == "75":
            self.adresses["75116"] = self.adresses["75016"]
        self.loaded.append(dept)

    def geocode(self, adress, postcode=None):

      # Look for postcode in adress if not provided in input
        if not postcode:
            postcode, adress = split_postcode(adress)
        if not postcode:
            if self.verbose:
                sys.stderr.write("[ERROR] Could not find a postcode in adress %s\n" % adress)
            return

      # Look for street number in adress
        number, street = split_number(adress)
        return self.find_street(postcode, street, number)

    def find_street(self, postcode, street, number=""):

      # Identify department from postcode and load bano data if needed
        postcode = clean_blanks(str(postcode))
        if postcode.startswith("20") and 20 not in self.loaded:
            self._load_departement("2A")
            self._load_departement("2B")
        else:
            try:
                if postcode.startswith("97"):
                    if postcode[:3] not in self.loaded:
                        self._load_departement(postcode[:3])
                elif postcode[:2] not in self.loaded:
                    self._load_departement(postcode[:2])
            except Exception as e:
                if self.verbose:
                    sys.stderr.write('%s while searching %s %s\n' % (e, number, street))
                return

      # Cleanup adress to match it with bano data
        street = hash_adress(street)
        ruestreet = "rue%s" % street
        try:    adresses = self.adresses[postcode][street]
        except:
          try:  adresses = self.adresses[postcode][ruestreet]
          except:
            othercodes = [(abs(digitize(c)-digitize(postcode)), c) for c in self.adresses.keys() if street in self.adresses[c] or ruestreet in self.adresses[c]]
            if othercodes:
                _, postcode = min(othercodes)
                if street not in self.adresses[postcode]:
                    street = ruestreet
                adresses = self.adresses[postcode][street]
            else:
                if self.verbose:
                    sys.stderr.write('[ERROR] Could not find a street "%s" with postcode %s in bano data\n' % (street, postcode))
                return

      # Return coordinates for the center of the street if no number
        digits = [(digitize(k), k) for k in adresses.keys()]
        number = clear_blanks(str(number))
        if not number:
            _, key = sorted(digits)[len(digits)/2]
            return adresses[key]

      # Return coordinates of matched adress
        if number in adresses:
            return adresses[number]

      # Return coordinates of closest number in the street with same side priority
        number = digitize(number)
        impair = number % 2
        dig_impa = [(abs(d-number), d2) for d,d2 in digits if d % 2]
        dig_pair = [(abs(d-number), d2) for d,d2 in digits if not (d % 2)]
        if dig_impa and (impair or not dig_pair):
            _,key = min(dig_impa)
        else:
            _,key = min(dig_pair)
        return adresses[key]


re_digit = re.compile(r"\D")
digitize = lambda x: int(re_digit.sub("", x))

re_clean_blanks = re.compile("[,. \s\t\r\n]+")
clear_blanks = lambda x: re_clean_blanks.sub("", x).strip().lower()
def clean_blanks(s):
    try:
        s = s.decode("utf-8")
    except:
        pass
    return re_clean_blanks.sub(" ", s).strip().lower()

re_postcode = re.compile(r"^(.*?) (\d{5})( |$)")
def split_postcode(adress):
    adress = clean_blanks(adress)
    if not re_postcode.match(adress):
        return "", adress
    res = re_postcode.search(adress)
    return res.group(2), res.group(1)

re_number = re.compile(r"^\D*(\d+)(?:[ -/]+\d+)?(\s*(?:b|t|q|(?:bis|ter|qua)+) )?(.*)$")
def split_number(adress):
    adress = clean_blanks(adress)
    if not re_number.match(adress):
        return "", adress
    res = re_number.search(adress)
    number = res.group(1)
    if res.group(2):
        number += res.group(2).strip()
    return number, res.group(3)

re_a = re.compile(ur'[àâä]')
re_e = re.compile(ur'[éèêë]')
re_i = re.compile(ur'[îï]')
re_o = re.compile(ur'[ôö]')
re_u = re.compile(ur'[ùûü]')
re_rue = re.compile(r'(^| )r[eu]* ')
re_rte = re.compile(r'(^| )r[te]+ ')
re_imp = re.compile(r'(^| )imp[as]* ')
re_bld = re.compile(r'(^| )b[lvrd]* ')
re_fbg = re.compile(r'(^| )f[auxborg]* ')
re_plc = re.compile(r'(^| )pl[ace]* ')
re_squ = re.compile(r'(^| )sq[uare]* ')
re_lot = re.compile(r'(^| )lot[isment]* ')
re_rdp = re.compile(r'(^| )r[ond\- ]*p[oint]* ')
re_ave = re.compile(r'(^| )ave? ')
re_ale = re.compile(r'(^| )al+ ')
re_st  = re.compile(r'(^| )st[- ]+')
re_ss  = re.compile(r' (ss|/s) ')
re_sur = re.compile(r' (sr|s/) ')
re_de  = re.compile(r" d((e l)?[' ]|[eu]( la|s)? )")
re_all = re.compile(r'\W')
def hash_adress(s):
    s = clean_blanks(s)
    s = re_a.sub("a", s)
    s = re_e.sub("e", s)
    s = re_i.sub("i", s)
    s = re_o.sub("o", s)
    s = re_u.sub("u", s)
    s = s.replace(u"ç", "c")
    s = re_rue.sub(" rue ", s)
    s = re_rte.sub(" route ", s)
    s = re_squ.sub(" square ", s)
    s = re_imp.sub(" impasse ", s)
    s = re_bld.sub(" boulevard ", s)
    s = re_lot.sub(" lotissement ", s)
    s = re_rdp.sub(" rond-point ", s)
    s = re_fbg.sub(" faubourg ", s)
    s = re_ave.sub(" avenue ", s)
    s = re_ale.sub(" allee ", s)
    s = re_plc.sub(" place ", s)
    s = re_st.sub(" saint ", s)
    s = re_ss.sub(" sous ", s)
    s = re_sur.sub("sur ", s)
    s = re_de.sub(" ", s)
    s = s.replace(" dr ", " docteur ")
    s = s.replace(" gen ", " general ")
    return re_all.sub("", s)
