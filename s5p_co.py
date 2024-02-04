# gee code: https://code.earthengine.google.com/1ca5cbc33cc553efce6f79b59e92ed13

import ee 
ee.Initialize()

############## Functions to Call ################/

aoi_global = ee.Geometry.Polygon([[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180, -90]]], None, False)
crs = 'EPSG:4326'
crsTransform = [0.1, 0, -180, 0, -0.1, 90]

def group_ImgCol(imgcollection, group_level='monthly'):
    mode_dict = {'daily': 10, 'monthly': 7, 'yearly': 4}

    """ group images by date """
    imgCol = imgcollection.sort("system:time_start")
    set_S5P_group_index = lambda img: img.set('GROUP_INDEX', img.date().format().slice(0, mode_dict[group_level]))
    imgCol = imgCol.map(set_S5P_group_index)

    d = imgCol.distinct(['GROUP_INDEX'])
    di = ee.ImageCollection(d)
    # Join collection to itself grouped by date
    date_eq_filter = ee.Filter.equals(leftField = 'GROUP_INDEX', rightField = 'GROUP_INDEX') 
    
    saveall = ee.Join.saveAll("to_mosaic")
    j = saveall.apply(di, imgCol, date_eq_filter)
    ji = ee.ImageCollection(j)
    
    # original_proj = ee.Image(ji.first()).select(0).projection()
    
    def mosaic_grouped_image(img):
        mosaiced = ee.ImageCollection.fromImages(img.get('to_mosaic')).mean()
        return (ee.Image(mosaiced).updateMask(1)#.copyProperties(img,img.propertyNames())
                .set('system:footprint', aoi_global)
                .setDefaultProjection(crs='EPSG:4326', scale=1000)
                .copyProperties(img, ['system:time_start'])
            )
    
    imgcollection_grouped = ji.map(mosaic_grouped_image)
    
    # imgCol_renamed = imgcollection_grouped.map(L8_bandRename)
    return ee.ImageCollection(imgcollection_grouped.copyProperties(imgCol, imgCol.propertyNames()))

def create_sentinel_5p_animation(aoi, start_date, end_date, group_level='monthly'):
    """ create_sentinel_5p_animation(aoi, start_date, end_date, group_level=10)
    
    create Sentinel-5P CO animation by aoi, start date, end date, and group level

    Parameters
    ----------
    aoi : {ee.Geometry}
        area of interest
    start_date : str
        start date, like 2023-01-01.
    
    end_date: str
        end date, like 2023-06-01
    
    group_level: 
        images will be group by the specified group level, date format 2023-01-01T05:03:01, YYYY-MM-DDThh:mm:ss
        group_level = 13: group by hour
        group_level = 10: group by day
        group_level = 7: group by month
    """
    
    S5P_flt = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_CO").select('CO_column_number_density') \
                .filterDate(start_date, end_date)

    band_viz = {
        "bands": 'CO_column_number_density',
        "min": 0,
        "max": 0.05,
        "palette": ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
    }

    # FAO Country Boundary
    FAO = ee.FeatureCollection('FAO/GAUL/2015/level0')

    # Paint country feature edges to the empty image.
    empty = ee.Image().byte()
    global_outline = (empty \
                .paint(featureCollection=FAO, color=1, width= 1) 
                # Convert to an RGB visualization image set line color to black.
                .visualize(palette= 'white', opacity= 0.7)
            )

    def vis_band(img): return img._apply_visualization(band_viz)[0].blend(global_outline)
    
    # "group by" date
    S5P_grouped = group_ImgCol(S5P_flt, group_level).map(vis_band)

    print("S5P_grouped ImageCollection Size: ", S5P_grouped.size().getInfo())


    # Print the animation to the console as a ui.Thumbnail using the above defined
    # arguments. Note that ui.Thumbnail produces an animation when the first input
    # is an ee.ImageCollection instead of an ee.Image.
    # print(ui.Thumbnail(S5P_grouped, videoArgs))

    # Alternatively, print a URL that will produce the animation when accessed.
    
    url =  S5P_grouped.getVideoThumbURL(params = {
            "dimensions": 768,
            "region": aoi,
            "framesPerSecond": 5,
            "crs": 'EPSG:3857',
        })
    
    # print(f"download url: {url}")
    return url
        

if __name__ == "__main__":

    # Sentinel 5P CO Dataset

    
    aoi = ee.Geometry.Polygon([[[-179.0, 86.0], [-179.0, -58.0], [179.0, -58.0], [179.0, 86.0]]], None, False)
    start_date = "2023-08-01"
    end_date = ee.Date(start_date).advance(1, 'month')
    print(start_date, end_date.format().slice(0,10).getInfo())
    
    url = create_sentinel_5p_animation(aoi, start_date, end_date, group_level=10)
    
    from download import Downloader
    downloader = Downloader()
    downloader.download(url, save_folder="./data", save_name='aug_daily.gif')
    



