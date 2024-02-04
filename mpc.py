
#%%
import os, time
import pystac
import pystac_client
import planetary_computer
from pathlib import Path

import rioxarray
import xarray as xr
from prettyprinter import pprint


# # create a Region of Interest (roi) in https://geojson.io/ or other platform, copy and paster coordinates
# roi = dict(type = "Polygon", coordinates = [...])

# Geometry of Colombia Country
minlon, minlat, maxlon, maxlat = -79.70677443301699, -3.635295809423141, -67.29293287446059, 12.831456778731706
roi = dict(type = "Polygon", coordinates = [[[minlon, minlat], [minlon, maxlat], [maxlon, maxlat], [maxlon, minlat], [minlon, minlat]]])

# Planetary computer's STAC URL
URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
catalog = pystac_client.Client.open(URL)

# query by geometry
items = catalog.search(
    intersects=roi,
    collections=["cop-dem-glo-30"]
    ).item_collection()

# # get the list of queried tiles 
# ids = [item['id'][:-4] for item in items.to_dict()['features']]
# print(f"The total number of dem tiles: {len(ids)}")
# pprint(ids)


#%%