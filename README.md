Map-Immo / python geocoder with BANO
====================================

Toutes les agences immobilières parisiennes de SeLoger.com geocodées via BANO

Données consultables ici : [https://github.com/RouxRC/map-immo/blob/master/agences.tsv](https://github.com/RouxRC/map-immo/blob/master/agences.tsv)
Et visualisées grâce à uMap ici : [https://umap.openstreetmap.fr/fr/map/map-immo-paris_16133](https://umap.openstreetmap.fr/fr/map/map-immo-paris_16133)

Ce code est publié sous licence GPL v3 et les données sous [http://www.vvlibri.org/fr/licence/odbl/10/fr/legalcode](licence ODBL). Elles ont été scrappées sur [http://www.seloger.com](SeLoger.com) et géolocalisées grâce à [https://github.com/osm-fr/bano-data/](Bano d'OpenStreetMap).

Le geocoder python employé est réutilisable en utilisant simplement le fichier `geocode.py` sans rien de plus. les données bano requises sont téléchargées à la volées et cachées dans un dossier `.cache`.

Par exemple :

```python
# import the GeoCoder class
from geocode import GeoCoder

# instantiate it
G = GeoCoder()
# optionnally make it verbose on errors
G = GeoCoder(verbose=True)

# geocode an adress
G.geocode("16, rue Pierre Lescot 75001 Paris")
> (48.86219, 2.348475)
# optionnally get fixed postcode returned
# note it will try and fix possible wrong postcodes by looking through others
G.geocode("16 r Pierre Lescot 75003 Paris", return_postcode=True)
> (75001, 48.86219, 2.348475)

# provide preknown postcode
G.geocode("16 Pierre Lescot", 75001)
> (48.86219, 2.348475)
# provide preknown details with lower level find_street function
# note the handling of street types such as rue, blvd, etc. is handled blurily
G.find_street(75001, "reu Pierre Lescot", 16)
> (48.86219, 2.348475)
# although providing wrong street names won't be handled automatically
# the result on mismatch will be None instead of a tuple
# and in verbose mode an error will be displayed in stderr
G.geocode("16 r Piere Lescot 75003 Paris", return_postcode=True)
> [ERROR] Could not find a street "ruepierelescot" with postcode 75003 in bano data
> 

# adresses with no number will return coordinates for the middle of the street
G.geocode("Pierre Lescot", 75001)
> (48.863034, 2.34866)
# adress with number missing from Bano data will return coordinates from the 
# closest existing number, priorily on the same side of the street
G.geocode("160 Pierre Lescot 75001")
> (48.864977, 2.330415)

# Data from multiple departments can quickly increase ram used
# For lighter but slower runs, you can preload a department's data on initiate
G = GeoCoder(69, verbose=True)
> [INFO] Downloading bano data for dept 69
G.loaded
> ['69']
# and reset loaded departement data when changing departement
G.set_departement(13)
> [INFO] Downloading bano data for dept 13
G.loaded
> ['13']
# other departments data will be loaded when needed anyway
G.find_street(75001, "rue pierre  lescot")
> [INFO] Downloading bano data for dept 75
> (48.863034, 2.34866)
G.loaded
> ['13', '75']
```
