#!/usr/bin/python3
import csv
import os
import subprocess
import re
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

xymon = os.getenv("XYMON")
xymsrv = os.getenv("XYMSRV")

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, executable_path="/usr/bin/geckodriver", service_log_path="/tmp/geckodriver.log")

checks = {
    "northernclimatereports.org": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": """
               return _.reduce(document.querySelectorAll('.report--temperature tbody td'), (acc, cur) => {
                    let temperature = parseFloat(cur.textContent.match(/[0-9\.]+(?=\u00b0F)/)[0])
                    return acc && _.inRange(temperature, 0, 100)
                })
            """,
            "text": "Temperature table values are valid."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#temp-chart .legend .traces').length > 5",
            "text": "Temperature chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": """
                return _.reduce(document.querySelectorAll('#precipitation tbody td'), (acc, cur) => {
                    let precipitation = parseFloat(cur.textContent.match(/[0-9\.]+(?=in)/)[0])
                    return acc && _.inRange(precipitation, 0, 20)
                })
            """,
            "text": "Precipitation table values are valid."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#precip-chart .legend .traces').length > 5",
            "text": "Precipitation chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": """
                return _.filter(document.querySelectorAll('#permafrost .leaflet-tile-loaded'), (tile) => {
                    return tile.src.indexOf('gipl') != -1
                }).length > 20
            """,
            "text": "Permafrost mini-maps loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#permafrost-alt-thaw-chart .legend .traces').length > 5",
            "text": "Permafrost active layer thickness chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#permafrost-alt-freeze-chart .legend .traces').length > 5",
            "text": "Permafrost ground freeze depth chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": """
                return _.filter(document.querySelectorAll('#wildfire .leaflet-tile-loaded'), (tile) => {
                    return tile.src.indexOf('flammability') != -1
                }).length > 20
            """,
            "text": "Flammability mini-maps loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#wildfire-flammability-chart .legend .traces').length > 5",
            "text": "Flammability chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": """
                return _.filter(document.querySelectorAll('#wildfire .leaflet-tile-loaded'), (tile) => {
                    return tile.src.indexOf('vegetation') != -1
                }).length > 20
            """,
            "text": "Vegetation type mini-maps loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#wildfire-veg-change-chart .legend .traces').length > 5",
            "text": "Vegetation type chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#precip-chart .legend .traces').length > 5",
            "text": "Precipitation chart is populated."
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/temperature/point/65.0628/-146.1627?format=csv",
            "text": "Temperature API endpoint CSV is valid."
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/precipitation/point/65.0628/-146.1627?format=csv",
            "text": "Precipitation API endpoint CSV is valid."
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/permafrost/point/65.0628/-146.1627?format=csv",
            "text": "Permafrost API endpoint CSV is valid."
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/alfresco/flammability/point/65.0628/-146.1627?format=csv",
            "text": "Flammability API endpoint CSV is valid."
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/alfresco/veg_type/point/65.0628/-146.1627?format=csv",
            "text": "Vegetation type API endpoint CSV is valid."
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/taspr/point/65.0628/-146.1627",
            "text": "Temperature and precipitation API endpoint JSON is valid."
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/permafrost/point/65.0628/-146.1627",
            "text": "Permafrost API endpoint JSON is valid."
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/alfresco/flammability/point/65.0628/-146.1627",
            "text": "Flammability API endpoint JSON is valid."
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "http://ec2-52-34-170-176.us-west-2.compute.amazonaws.com/alfresco/veg_type/point/65.0628/-146.1627",
            "text": "Vegetation type API endpoint JSON is valid."
        }
    ],
    "production-fire-tally.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "javascript": "return document.querySelectorAll('#tally .legendlines').length > 5",
            "text": "Statewide daily tally chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "javascript": "return document.querySelectorAll('#tally-zone .legendlines').length > 5",
            "text": "Daily tally by protection chart graph is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "javascript": "return document.querySelectorAll('#tally-year .legendlines').length > 5",
            "text": "Daily tally by year chart is populated."
        },
    ],
    "arcticeds.org": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/climate/precipitation",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Precipitation map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=annual_precip_totals_mm&styles=precip_mm_midcentury_era&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_precip&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected precipitation map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/climate/snowfall",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Snowfall map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=mean_annual_snowfall_mm&styles=snowfall_mm&format=image%2Fpng&transparent=true&version=1.3.0&id=future_mean_annual_snowfall&dim_model=4&dim_scenario=3&dim_decade=18&width=256&height=256&crs=EPSG%3A3338&bbox=70586,969097,594874,1493385",
            "text": "Projected snowfall map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/climate/temperature",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Temperature map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=annual_mean_temp&styles=temp_midcentury_era&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_annual_mean_temp&width=256&height=256&crs=EPSG%3A3338&bbox=70586,969097,594874,1493385",
            "text": "Projected mean annual temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/engineering/design-freezing-index",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Design freezing index map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=design_freezing_index&styles=arctic_eds&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_design_freezing_index&dim_model=2&dim_era=2&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected design freezing index map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/engineering/design-thawing-index",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Design thawing index map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=design_thawing_index&styles=arctic_eds&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_design_thawing_index&dim_model=2&dim_era=2&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected design thawing index map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/engineering/freezing-index",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Freezing index map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=freezing_index&styles=arctic_eds_freezing_index_future_condensed&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_freezing_index_midcentury&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected freezing index map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/engineering/thawing-index",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Thawing index map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=thawing_index&styles=arctic_eds_thawing_index_future_condensed_compressed&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_thawing_index_midcentury&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected thawing index map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/engineering/heating-degree-days",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Heating degree days map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=heating_degree_days&styles=arctic_eds_heating_degree_days_future_condensed_compressed&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_heating_degree_days&dim_model=2&dim_era=2&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected heating degree days map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/physiography/ecoregions",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Ecoregions map loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/physiography/geology",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Geology map loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/physiography/permafrost",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Permafrost map loaded."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=permafrost_beta%3Aobu_pf_extent&styles=&format=image%2Fpng&transparent=true&version=1.3.0&id=pfextent_obu&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Permafrost extent (Obu) map layer accessible."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/climate/temperature/report/63.1429/-154.9583#report",
            "javascript": """
               return _.reduce(document.querySelectorAll('#report tbody td'), (acc, cur) => {
                    let temperature = parseFloat(cur.textContent.match(/[0-9\.]+(?=\u00b0F)/)[0])
                    return acc && _.inRange(temperature, -80, 120)
                })
            """,
            "text": "Temperature table populated."
        },
    ],
    "seaiceatlas.snap.uaf.edu": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://www.snap.uaf.edu/tools/sea-ice-atlas",
            "javascript": "return document.querySelectorAll('#map--main .leaflet-tile-loaded').length > 20",
            "text": "Sea ice map loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://www.snap.uaf.edu/tools/sea-ice-atlas",
            "click": "#map--main",
            "javascript": "return document.querySelectorAll('.js-line').length > 0",
            "text": "Sea ice chart populated."
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/seaice/point/67.19/-167.69/",
            "text": "Sea ice API endpoint JSON is valid."
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/seaice/point/67.19/-167.69?format=csv",
            "text": "Sea ice API endpoint CSV is valid."
        },
    ],
    "production-wrcc-wind-tool.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#map canvas').length > 1",
            "text": "Airport map loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#rose g').length > 100",
            "text": "Rose chart populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#rose_monthly g').length > 1000",
            "text": "Rose monthly charts populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#exceedance_plot g').length > 80",
            "text": "Exceedence chart populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#wep_box path').length > 15",
            "text": "Wind energy potential chart populated."
        },
    ],
    "production-usda-dash.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/gardenhelper",
            "javascript": "return document.querySelectorAll('#tcharts g').length > 100",
            "text": "Growing season chart populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/gardenhelper",
            "click": ".tab:nth-of-type(2)",
            "javascript": "return document.querySelectorAll('#acharts path').length > 1000",
            "text": "Annual minimums chart populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/gardenhelper",
            "click": ".tab:nth-of-type(3)",
            "javascript": "return document.querySelectorAll('#ccharts .legendlines').length > 10",
            "text": "Growing degree days chart populated."
        },
    ],
    "production-alaska-wildfires.s3-website-us-west-2.amazonaws.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/alaska-wildfires",
            "javascript": "return document.querySelectorAll('#map--leaflet-map path').length > 1",
            "text": "Wildfire map populated."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=postgis_lightning&styles=&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=postgis_lightning&width=256&height=256&crs=EPSG%3A3338&bbox=594874,969097506,1119162,1493385",
            "text": "Lightning strikes map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aspruceadj_3338&styles=alaska_wildfires%3Aspruce_adjective&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=spruceadj_3338&width=256&height=256&crs=EPSG%3A3338&bbox=-453701,444809,70586,969097",
            "text": "Fire danger ratings map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Asnow_cover_3338&styles=alaska_wildfires%3Asnow_cover&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=snow_cover_3338&width=256&height=256&crs=EPSG%3A3338&bbox=-453701,969097,70586,1493385",
            "text": "Snow cover map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aalaska_landcover_2015&styles=&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=alaska_landcover_2015&width=256&height=256&crs=EPSG%3A3338&bbox=-453701,969097,70586,1493385",
            "text": "Land cover types map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Alightning-monthly-climatology&styles=&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=2015-5-01T00%3A00%3A00Z&id=gridded_lightning&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical lightning strikes map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=historical_fire_perimiters&styles=historical_fire_polygon_buckets&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=historical_fire_perimiters&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical fire perimeters map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aalfresco_relative_flammability_cru_ts40_historical_1900_1999_iem&styles=flammability&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=alfresco_relative_flammability_cru_ts40_historical_1900_1999_iem&width=256&height=256&crs=EPSG%3A3338&bbox=594874,1493385,1119162,2017673",
            "text": "Historical modeled flammability map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aalfresco_relative_flammability_NCAR-CCSM4_rcp85_2000_2099&styles=flammability&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=alfresco_relative_flammability_NCAR-CCSM4_rcp85_2000_2099&width=256&height=256&crs=EPSG%3A3338&bbox=594874,1493385,1119162,2017673",
            "text": "Projected flammability map layer accessible."
        },
    ],
    "production22222.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://www.snap.uaf.edu/tools/nwt-climate-explorer",
            "javascript": "return document.querySelectorAll('#minesites-map canvas').length > 1",
            "text": "Location map loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://www.snap.uaf.edu/tools/nwt-climate-explorer",
            "javascript": "return document.querySelectorAll('#my-graph .legendlines').length > 1",
            "text": "Temperature chart populated."
        },
    ],
    "production-dash-cc.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/community-charts",
            "javascript": "return document.querySelectorAll('#ccharts g').length > 100",
            "text": "Average temperature chart populated."
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://snap.uaf.edu/tools/community-charts/dash/dlCSV?value=AK124",
            "text": "Community charts CSV is valid."
        },
    ],
    "permafrost-production.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/permafrost",
            "javascript": "return document.querySelectorAll('#weather-plot path.point').length > 3",
            "text": "Permafrost risk chart populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/permafrost",
            "javascript": "return document.querySelectorAll('#community-table tr').length > 1",
            "text": "Permafrost risk table populated."
        },
    ],
    "windtool.accap.uaf.edu": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#map canvas').length > 1",
            "text": "Location map loaded."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#means_box path.box').length > 5",
            "text": "Monthly wind speed plot populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#rose g').length > 100",
            "text": "Wind speed plot populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#rose_monthly g').length > 1000",
            "text": "Monthly wind speed plot populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#threshold_graph g').length > 100",
            "text": "Modeled wind duration plot populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#future_delta_percentiles_graph g').length > 100",
            "text": "Modeled past and future wind plot populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#future_rose g').length > 500",
            "text": "Modeled wind speed plot populated."
        },
    ],
}

def javascriptTest(check):
    try:
        driver.get(check["url"])
        time.sleep(10)
        if "click" in check:
            elementToClick = driver.find_element(By.CSS_SELECTOR, check["click"])
            elementToClick.click()
            time.sleep(10) 
        return driver.execute_script(check["javascript"])
    except:
        return False


def csvTest(check):
    try:
        response = requests.get(check["url"])
        no_metadata = []
        for row in response.text.split("\r\n"):
            if len(row) > 0 and row[0] != "#":
                no_metadata.append(row)
        reader = csv.reader(no_metadata)
        next(reader)
        return True
    except:
        return False


def jsonTest(check):
    try:
        response = requests.get(check["url"])
        results = response.json()
        return True
    except:
        return False


def urlTest(check):
    try:
        response = requests.get(check["url"])
        return response.status_code == 200
    except:
        return False


for machine in checks.keys():
    colors = {}
    messages = {}
    for check in checks[machine]:
        column = check["column"]
        if check["column"] not in colors:
            colors[column] = "green"
            messages[column] = ""

        if check["type"] == "javascript":
            success = javascriptTest(check)
        elif check["type"] == "json":
            success = jsonTest(check)
        elif check["type"] == "csv":
            success = csvTest(check)
        elif check["type"] == "url":
            success = urlTest(check)

        if success == True:
            messages[column] += "&green " + check["text"] + "\n"
        else:
            colors[column] = "red"
            messages[column] += "&red " + check["text"] + "\n"

    for column in colors.keys():
        date = subprocess.check_output(["date"]).decode("ascii")
        machine_safe = machine.replace(".", ",")
        status = "status {}.{} {} {}\n{}".format(
            machine,
            column,
            colors[column],
            date,
            messages[column]
        )
        subprocess.call([xymon, xymsrv, status])

driver.quit()
