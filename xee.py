#%%
import ee
import xarray
ee.Initialize()

i = ee.ImageCollection(ee.Image("LANDSAT/LC08/C02/T1_TOA/LC08_044034_20140318"))
roi = ee.Geometry.Polygon(
        [[[-122.80785566930156, 38.08703151999987],
          [-122.80785566930156, 37.357077777161805],
          [-121.89599043492656, 37.357077777161805],
          [-121.89599043492656, 38.08703151999987]]], None, False)

print(i.first().select(0).projection().getInfo())

ds = xarray.open_dataset(i, 
                         engine='ee', 
                         projection=i.first().select(0).projection(),
                         crs='EPSG:32610',
                        #  geometry= i.first().geometry(),
                         geometry=roi,
                         scale=30
                    )

ds
# %%

s2_imgCol = (ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
                  .filterDate('2022-01-01', '2022-01-31')
                  .filterBounds(ee.Geometry.Point([-121.52362180406335,40.13422437870105]))
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

    )

ds = xarray.open_dataset(s2_imgCol, 
                         engine='ee', 
                         projection=s2_imgCol.first().select(0).projection(),
                         crs='EPSG:32610',
                        #  geometry= i.first().geometry(),
                         geometry=s2_imgCol.first().geometry(),
                         scale=10,
                    )