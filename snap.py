#!/usr/bin/python3
import csv
import os
import subprocess
import random
import re
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

xymon = os.getenv("XYMON")
xymsrv = os.getenv("XYMSRV")

options = Options()
options.headless = True

# Load enough of the page to interact with it.
# Don't wait for straggler HTTP requests.
caps = DesiredCapabilities().FIREFOX
caps["pageLoadStrategy"] = "eager"

driver = webdriver.Firefox(
    desired_capabilities=caps,
    options=options,
    executable_path="/usr/bin/geckodriver",
    service_log_path="/tmp/geckodriver.log",
)
actions = ActionChains(driver)

tests = {
    "northernclimatereports.org": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#temperature tbody td span').length > 200",
            "text": "Temperature table is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#temp-chart .legend .traces').length > 5",
            "text": "Temperature chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('.report--temperature-indicators tbody td span').length > 80",
            "text": "Temperature indicators chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#precipitation tbody td span').length > 200",
            "text": "Precipitation table is populated",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#precip-chart .legend .traces').length > 5",
            "text": "Precipitation chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('.report--precipitation-indicators tbody td span').length > 80",
            "text": "Precipitation indicators chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#hydrology tbody td span').length > 200",
            "text": "Hydrology tables are populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#hydrology .leaflet-tile-loaded').length > 200",
            "text": "Hydrology mini-maps loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#permafrost .leaflet-tile-loaded').length > 40",
            "text": "Permafrost mini-maps loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#permafrost-top-chart .legend .traces').length > 3",
            "text": "Permafrost depth to top of permafrost chart is populated.",
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
            "text": "Flammability mini-maps loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#wildfire-flammability-chart .legend .traces').length > 5",
            "text": "Flammability chart is populated.",
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
            "text": "Vegetation type mini-maps loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#wildfire-veg-change-chart .legend .traces').length > 5",
            "text": "Vegetation type chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#climate-protection-beetles tbody td').length > 40",
            "text": "Climate protection from beetles tables are populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "javascript": "return document.querySelectorAll('#climate-protection-beetles .leaflet-tile-loaded').length > 40",
            "text": "Climate protection from beetles mini-maps loaded.",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/temperature/point/{lat}/{lon}?format=csv",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Temperature API endpoint CSV is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/precipitation/point/{lat}/{lon}?format=csv",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Precipitation API endpoint CSV is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/indicators/base/point/{lat}/{lon}?format=csv",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Indicators API endpoint CSV is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/eds/hydrology/point/{lat}/{lon}?format=csv",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Hydrology API endpoint CSV is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/permafrost/point/{lat}/{lon}?format=csv",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Permafrost API endpoint CSV is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/alfresco/flammability/local/{lat}/{lon}?format=csv",
            "lat_range": [63.72, 64.40],
            "lon_range": [-157.15, -154.20],
            "text": "Flammability API endpoint CSV is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/alfresco/veg_type/local/{lat}/{lon}?format=csv",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Vegetation type API endpoint CSV is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/beetles/point/{lat}/{lon}?format=csv",
            "lat_range": [64.55, 65.80],
            "lon_range": [-158, -156],
            "text": "Climate protection from beetles API endpoint CSV is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/taspr/point/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Temperature and precipitation API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/indicators/base/point/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Indicators API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/eds/hydrology/point/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Hydrology API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/permafrost/point/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Permafrost API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/alfresco/flammability/local/{lat}/{lon}",
            "lat_range": [63.72, 64.40],
            "lon_range": [-157.15, -154.20],
            "text": "Flammability API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/alfresco/veg_type/local/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Vegetation type API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/beetles/point/{lat}/{lon}",
            "lat_range": [64.55, 65.80],
            "lon_range": [-158, -156],
            "text": "Climate protection from beetles API endpoint JSON is valid ({lat}, {lon}).",
        },
    ],
    "production-fire-tally.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "javascript": "return document.querySelectorAll('#tally .legendlines').length > 5",
            "text": "Statewide daily tally chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "javascript": "return document.querySelectorAll('#tally-zone .legendlines').length > 5",
            "text": "Daily tally by protection chart graph is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "javascript": "return document.querySelectorAll('#tally-year .legendlines').length > 5",
            "text": "Daily tally by year chart is populated.",
        },
    ],
    "arcticeds.org": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/report/{lat}/{lon}",
            "lat_range": [62, 62.5],
            "lon_range": [-156, -153],
            "javascript": "return document.querySelectorAll('.precipitation table td').length > 300",
            "text": "Precipitation section loaded ({lat}, {lon}).",
            "delay": 480,
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/report/{lat}/{lon}",
            "lat_range": [62, 62.5],
            "lon_range": [-156, -153],
            "javascript": "return document.querySelectorAll('.pf table td').length > 100",
            "text": "Precipitation frequency section loaded ({lat}, {lon}).",
            "delay": 10,
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/report/{lat}/{lon}",
            "lat_range": [62, 62.5],
            "lon_range": [-156, -153],
            "javascript": "return document.querySelectorAll('.temperature table td').length > 100",
            "text": "Temperature section loaded ({lat}, {lon}).",
            "delay": 10,
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/report/{lat}/{lon}",
            "lat_range": [62, 62.5],
            "lon_range": [-156, -153],
            "javascript": "return document.querySelectorAll('.temperature-index table td').length > 100",
            "text": "Temperature index section loaded ({lat}, {lon}).",
            "delay": 10,
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/report/{lat}/{lon}",
            "lat_range": [62, 62.5],
            "lon_range": [-156, -153],
            "javascript": "return document.querySelectorAll('.permafrost table td').length > 100",
            "text": "Permafrost section loaded ({lat}, {lon}).",
            "delay": 10,
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/maps",
            "javascript": "return document.querySelectorAll('#precipitation .leaflet-tile-loaded').length > 20",
            "text": "Precipitation map loaded.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://maps.earthmaps.io/rasdaman/ows?service=WMS&request=GetMap&layers=annual_precip_totals_mm&styles=precip_mm_midcentury_era&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_precip&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected precipitation map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/maps",
            "javascript": "return document.querySelectorAll('#permafrost .leaflet-tile-loaded').length > 20",
            "text": "Permafrost map loaded.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=permafrost_beta%3Aobu_pf_extent&styles=&format=image%2Fpng&transparent=true&version=1.3.0&id=pfextent_obu&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Permafrost extent (Obu) map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://arcticeds.org/maps",
            "javascript": "return document.querySelectorAll('#temperature .leaflet-tile-loaded').length > 20",
            "text": "Temperature map loaded.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://maps.earthmaps.io/rasdaman/ows?service=WMS&request=GetMap&layers=annual_mean_temp&styles=temp_midcentury_era&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_annual_mean_temp&width=256&height=256&crs=EPSG%3A3338&bbox=70586,969097,594874,1493385",
            "text": "Projected mean annual temperature map layer accessible.",
        },
    ],
    "seaiceatlas.org": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://seaiceatlas.org",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Sea ice map loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://seaiceatlas.org",
            "click": "#map",
            "click_x_offset": 800,
            "click_y_offset": 100,
            "javascript": "return document.querySelectorAll('.js-line').length > 0",
            "text": "Sea ice chart populated.",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/seaice/point/{lat}/{lon}/",
            "lat_range": [71.50, 73.60],
            "lon_range": [-177.5, -131.41],
            "text": "Sea ice API endpoint JSON is valid.",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://earthmaps.io/seaice/point/{lat}/{lon}?format=csv",
            "lat_range": [71.50, 73.60],
            "lon_range": [-177.5, -131.41],
            "text": "Sea ice API endpoint CSV is valid at {lat}, {lon}.",
        },
    ],
    "production-wrcc-wind-tool.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#map canvas').length > 1",
            "text": "Airport map loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#rose g').length > 100",
            "text": "Rose chart populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#rose_monthly g').length > 1000",
            "text": "Rose monthly charts populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#exceedance_plot g').length > 80",
            "text": "Exceedence chart populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/airport-winds",
            "javascript": "return document.querySelectorAll('#wep_box path').length > 15",
            "text": "Wind energy potential chart populated.",
        },
    ],
    "production-usda-dash.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/gardenhelper",
            "javascript": "return document.querySelectorAll('#tcharts g').length > 100",
            "text": "Growing season chart populated.",
            "delay": 60,
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/gardenhelper",
            "click": ".tab:nth-of-type(2)",
            "javascript": "return document.querySelectorAll('#acharts path').length > 1000",
            "text": "Annual minimums chart populated.",
            "delay": 120,
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/gardenhelper",
            "click": ".tab:nth-of-type(3)",
            "javascript": "return document.querySelectorAll('#ccharts .legendlines').length > 10",
            "text": "Growing degree days chart populated.",
            "delay": 60,
        },
    ],
    "alaskawildfires.org": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://alaskawildfires.org",
            "javascript": "return document.querySelectorAll('#map--leaflet-map div').length > 10 || document.querySelectorAll('.intro').length == 0",
            "text": "Wildfire map loaded or inactive.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/alaska-wildfires",
            "javascript": "return document.querySelectorAll('#map--leaflet-map div').length > 10 || document.querySelectorAll('.intro').length == 0",
            "text": "Wildfire map redirects to https://alaskawildfires.org.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/alaska_wildfires/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Afire_points&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=false&crs=EPSG%3A3338&width=256&height=256&bbox=594874,1493385,1119162,2017673",
            "text": "Fire points map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/alaska_wildfires/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Afire_polygons&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=false&crs=EPSG%3A3338&width=256&height=256&bbox=594874,1493385,1119162,2017673",
            "text": "Fire polygons map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/alaska_wildfires/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aviirs_hotspots&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=false&crs=EPSG%3A3338&width=256&height=256&bbox=594874,1493385,1119162,2017673",
            "text": "VIIRS hotspots map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Alightning_strikes&styles=&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&width=256&height=256&crs=EPSG%3A3338&bbox=594874,1493385,1119162,2017673",
            "text": "Lightning strikes map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/alaska_wildfires/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Apurple_air&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=false&crs=EPSG%3A3338&width=256&height=256&bbox=594874,1493385,1119162,2017673",
            "text": "Purple Air AQI sensors map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/alaska_wildfires/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aaqi_forecast_6_hrs&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=false&crs=EPSG%3A3338&width=256&height=256&bbox=594874,1493385,1119162,2017673",
            "text": "AQI 6 hour forecast map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/alaska_wildfires/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aaqi_forecast_12_hrs&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=false&crs=EPSG%3A3338&width=256&height=256&bbox=594874,1493385,1119162,2017673",
            "text": "AQI 12 hour forecast map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/alaska_wildfires/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aaqi_forecast_24_hrs&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=false&crs=EPSG%3A3338&width=256&height=256&bbox=594874,1493385,1119162,2017673",
            "text": "AQI 24 hour forecast map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/alaska_wildfires/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aaqi_forecast_48_hrs&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=false&crs=EPSG%3A3338&width=256&height=256&bbox=594874,1493385,1119162,2017673",
            "text": "AQI 48 hour forecast map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aspruceadj_3338&styles=alaska_wildfires%3Aspruce_adjective&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=spruceadj_3338&width=256&height=256&crs=EPSG%3A3338&bbox=-453701,444809,70586,969097",
            "text": "Fire danger ratings map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Aalaska_landcover_2015&styles=&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=alaska_landcover_2015&width=256&height=256&crs=EPSG%3A3338&bbox=-453701,969097,70586,1493385",
            "text": "Land cover types map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Alightning-monthly-climatology&styles=&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=2015-5-01T00%3A00%3A00Z&id=gridded_lightning&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical lightning strikes map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=historical_fire_perimiters&styles=historical_fire_polygon_buckets&format=image%2Fpng&transparent=true&version=1.3&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=historical_fire_perimiters&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical fire perimeters map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://maps.earthmaps.io/rasdaman/ows?service=WMS&request=GetMap&layers=alfresco_relative_flammability_30yr&styles=alaska_wildfire_explorer_historical&format=image%2Fpng&transparent=true&version=1.3.0&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=alfresco_relative_flammability_cru_ts40_historical_1950_2008_iem&dim_model=0&dim_scenario=0&width=256&height=256&crs=EPSG%3A3338&bbox=70586.06568358204,1493385.882955057,594874.0656835823,2017673.8829550678",
            "text": "Historical modeled flammability map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://maps.earthmaps.io/rasdaman/ows?service=WMS&request=GetMap&layers=alfresco_relative_flammability_30yr&styles=alaska_wildfire_explorer_projected&format=image%2Fpng&transparent=true&version=1.3.0&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=alfresco_relative_flammability_NCAR-CCSM4_rcp85_2070_2099&dim_model=6&dim_scenario=3&width=256&height=256&crs=EPSG%3A3338&bbox=70586.06568358204,1493385.882955057,594874.0656835823,2017673.8829550678",
            "text": "Projected flammability map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=all_boundaries%3Aall_gmus&styles=&format=image%2Fpng&transparent=true&version=1.3.0&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=gmu&dim_model=&dim_scenario=&width=256&height=256&crs=EPSG%3A3338&bbox=-453701.9343164183,969097.8829550534,70586.06568358072,1493385.8829550538",
            "text": "Game Management Units map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=all_boundaries%3Aall_protected_areas&styles=&format=image%2Fpng&transparent=true&version=1.3.0&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=protected_areas&dim_model=&dim_scenario=&width=256&height=256&crs=EPSG%3A3338&bbox=70586.06568358286,969097.882955058,594874.0656835833,1493385.8829550613",
            "text": "Protected Areas map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=all_boundaries%3Aall_fire_zones&styles=&format=image%2Fpng&transparent=true&version=1.3.0&continuousWorld=true&tiled=true&srs=EPSG%3A3338&time=&id=fire_zones&dim_model=&dim_scenario=&width=256&height=256&crs=EPSG%3A3338&bbox=70586.06568358286,969097.882955058,594874.0656835833,1493385.8829550613",
            "text": "Fire Management Units map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/fire/point/{lat}/{lon}",
            "lat_range": [62, 62.5],
            "lon_range": [-156, -153],
            "text": "Fire API endpoint JSON is valid ({lat}, {lon}).",
        },
    ],
    "production22222.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://www.snap.uaf.edu/tools/nwt-climate-explorer",
            "javascript": "return document.querySelectorAll('#minesites-map canvas').length > 1",
            "text": "Location map loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://www.snap.uaf.edu/tools/nwt-climate-explorer",
            "javascript": "return document.querySelectorAll('#my-graph .legendlines').length > 1",
            "text": "Temperature chart populated.",
        },
    ],
    "production-dash-cc.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/community-charts",
            "javascript": "return document.querySelectorAll('#ccharts g').length > 100",
            "text": "Average temperature chart populated.",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://snap.uaf.edu/tools/community-charts/dash/dlCSV?value=AK124",
            "text": "Community charts CSV is valid.",
        },
    ],
    "permafrost-production.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/permafrost",
            "javascript": "return document.querySelectorAll('#weather-plot path.point').length > 3",
            "text": "Permafrost risk chart populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/permafrost",
            "javascript": "return document.querySelectorAll('#community-table tr').length > 1",
            "text": "Permafrost risk table populated.",
        },
    ],
    "windtool.accap.uaf.edu": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#map canvas').length > 1",
            "text": "Location map loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#means_box path.box').length > 5",
            "text": "Monthly wind speed plot populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#rose g').length > 100",
            "text": "Wind speed plot populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#rose_monthly g').length > 1000",
            "text": "Monthly wind speed plot populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#threshold_graph g').length > 100",
            "text": "Modeled wind duration plot populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#future_delta_percentiles g').length > 80",
            "text": "Modeled past and future wind plot populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "http://windtool.accap.uaf.edu/",
            "javascript": "return document.querySelectorAll('#future_rose g').length > 500",
            "text": "Modeled wind speed plot populated.",
        },
    ],
    "living-off-the-land.s3-website-us-west-2.amazonaws.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/living-off-the-land",
            "javascript": "return document.querySelectorAll('#ice-and-snow__map path').length > 100",
            "text": "Ice observations map loaded.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=nasa_above%3Awintertemp_2010s_tcc&styles=&format=image%2Fpng&transparent=true&version=1.3&srs=EPSG%3A3338&tiled=true&continuousWorld=true&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Winter temperature (2010) map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/living-off-the-land",
            "javascript": "return document.querySelectorAll('#snowday-fraction-map__map path').length > 80",
            "text": "Snow observations map loaded.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=nasa_above%3AOct_snowdayfraction_2010s_tcc_reprojected&styles=&format=image%2Fpng&transparent=true&version=1.3&srs=EPSG%3A3338&tiled=true&continuousWorld=true&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Snow observations (2010) map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/living-off-the-land",
            "javascript": "return document.querySelectorAll('#permafrost-map__map path').length > 150",
            "text": "Permafrost map loaded.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=nasa_above%3AJuly_permafrost_2m_2010s_tcc&styles=&format=image%2Fpng&transparent=true&version=1.3&srs=EPSG%3A3338&tiled=true&continuousWorld=true&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Permafrost (2010) map layer accessible.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/living-off-the-land",
            "javascript": "return document.querySelectorAll('#historical-fires__map path').length > 40",
            "text": "Historical fire map loaded.",
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.earthmaps.io/geoserver/wms?service=WMS&request=GetMap&layers=alaska_wildfires%3Ahistorical_fire_perimiters&styles=fire_history_70s_2010s&format=image%2Fpng&transparent=true&version=1.3&srs=EPSG%3A3338&tiled=true&continuousWorld=true&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical fires map layer accessible.",
        },
    ],
    "production-swti.eba-spvr3kbd.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://accap.uaf.edu/tools/statewide-temperature-index",
            "javascript": "return document.querySelectorAll('#daily-index .traces').length > 1",
            "text": "Chart populated.",
        },
        {
            "column": "webapp",
            "type": "csv",
            "url": "https://accap.uaf.edu/tools/statewide-temperature-index/downloads/statewide_temperature_daily_index.csv",
            "text": "CSV is valid.",
        },
    ],
    "fish-and-fire.s3-website-us-west-2.amazonaws.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/fish-and-fire/",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 15",
            "text": "Location selector map loaded.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/fish-and-fire/report/fb653a",
            "javascript": "return document.querySelectorAll('#map path').length > 3",
            "text": "Polygon loaded on report page.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/fish-and-fire/report/fb653a",
            "javascript": "return document.querySelectorAll('#chart .legend .traces').length > 5",
            "text": "Riparian fire index chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/fish-and-fire/report/fb653a",
            "javascript": "return document.querySelectorAll('#hydro-stats-chart-1 .legend .traces').length > 1",
            "text": "Hydrology stats chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/fish-and-fire/report/fb653a",
            "javascript": "return document.querySelectorAll('#hydrograph-chart-1 .legend .traces').length > 1",
            "text": "Hydrograph chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/fish-and-fire/report/fb653a",
            "javascript": "return document.querySelectorAll('#stream-temp-chart-4 .legend .traces').length > 1",
            "text": "Stream temperature chart is populated.",
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/fish-and-fire/report/fb653a",
            "javascript": "return document.querySelectorAll('#fish-growth-chart-4 .legend .traces').length > 1",
            "text": "Fish growth chart is populated.",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://gs.earthmaps.io/geoserver/fish_and_fire/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=fish_and_fire%3AAOIs&outputFormat=application%2Fjson&PropertyName=(AOI_Name_,Category)",
            "text": "GeoServer returns valid JSON from shapefile.",
        },
    ],
    "arcticdatascience.org": [
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/cmip6/point/{lat}/{lon}?vars=tas",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "CMIP6 tas API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/indicators/cmip6/point/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "CMIP6 indicators API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/temperature_anomalies/point/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Temperature anomalies API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/permafrost/point/gipl/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Permafrost API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/alfresco/flammability/local/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Flammability API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/alfresco/veg_type/local/{lat}/{lon}",
            "lat_range": [62.70, 67.92],
            "lon_range": [-158.50, -144.21],
            "text": "Vegetation type API endpoint JSON is valid ({lat}, {lon}).",
        },
        {
            "column": "webapp",
            "type": "json",
            "url": "https://earthmaps.io/landfastice/point/{lat}/{lon}",
            "lat_range": [71, 71.5],
            "lon_range": [-150, -148],
            "text": "Landfast sea ice extent API endpoint JSON is valid ({lat}, {lon}).",
        },
    ],
}


def processCoords(test):
    if "lat_range" not in test or "lon_range" not in test:
        return test

    if "arcticeds.org" in test["url"]:
        # Generate coordinates once for arcticeds.org tests
        if not hasattr(processCoords, "arcticeds_coords"):
            lat_range = test["lat_range"]
            lon_range = test["lon_range"]
            processCoords.arcticeds_coords = {
                "lat": round(random.uniform(lat_range[0], lat_range[1]), 2),
                "lon": round(random.uniform(lon_range[0], lon_range[1]), 2),
            }
        coords = processCoords.arcticeds_coords
    else:
        lat_range = test["lat_range"]
        lon_range = test["lon_range"]
        coords = {
            "lat": round(random.uniform(lat_range[0], lat_range[1]), 2),
            "lon": round(random.uniform(lon_range[0], lon_range[1]), 2),
        }

    test["url"] = test["url"].format(**coords)
    test["text"] = test["text"].format(**coords)
    return test


def javascriptTest(test):
    try:
        if "delay" in test:
            delay = test["delay"]
        else:
            delay = 20
        driver.get(test["url"])
        time.sleep(delay)
        if "click" in test:
            element = driver.find_element(By.CSS_SELECTOR, test["click"])
            # Precisely position click inside element if necessary.
            if "click_x_offset" in test and "click_y_offset" in test:
                x_offset = test["click_x_offset"]
                y_offset = test["click_y_offset"]
                driver.execute_script("arguments[0].scrollIntoView();", element)
                actions.move_to_element_with_offset(
                    element, x_offset, y_offset
                ).click().perform()
            else:
                element.click()
            time.sleep(delay)
        return driver.execute_script(test["javascript"])
    except:
        return False


def csvTest(test):
    try:
        response = requests.get(test["url"])
        if response.status_code != 200:
            return False
        no_metadata = []
        for row in re.split("\r?\n", response.text):
            if len(row) > 0 and row[0] != "#":
                no_metadata.append(row)
        reader = csv.reader(no_metadata)
        next(reader)
        return True
    except:
        return False


def jsonTest(test):
    try:
        response = requests.get(test["url"])
        if response.status_code != 200:
            return False
        results = response.json()
        return True
    except:
        return False


def urlTest(test):
    try:
        response = requests.get(test["url"])
        return response.status_code == 200
    except:
        return False


for machine in tests.keys():
    colors = {}
    messages = {}
    for test in tests[machine]:
        column = test["column"]
        if test["column"] not in colors:
            colors[column] = "green"
            messages[column] = ""

        test = processCoords(test)

        if test["type"] == "javascript":
            success = javascriptTest(test)
        elif test["type"] == "json":
            success = jsonTest(test)
        elif test["type"] == "csv":
            success = csvTest(test)
        elif test["type"] == "url":
            success = urlTest(test)

        if success == True:
            messages[column] += "&green " + test["text"] + "\n"
        else:
            colors[column] = "red"
            messages[column] += "&red " + test["text"] + "\n"

    for column in colors.keys():
        date = subprocess.check_output(["date"]).decode("ascii")
        machine_safe = machine.replace(".", ",")
        status = "status {}.{} {} {}\n{}".format(
            machine, column, colors[column], date, messages[column]
        )
        subprocess.call([xymon, xymsrv, status])

driver.quit()
