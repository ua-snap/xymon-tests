#!/usr/bin/python3
import csv
import os
import subprocess
import re
import requests
import time
from selenium import webdriver
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
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=annual_mean_temp&styles=temp_midcentury_era&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_annual_mean_temp&width=256&height=256&crs=EPSG%3A3338&bbox=70586,969097,594874,1493385",
            "text": "Projected mean annual temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=jan_min_max_mean_temp&styles=temp_historical_january_min&format=image%2Fpng&transparent=true&version=1.3.0&id=historical_era_january_min&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical January minimum temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=july_min_max_mean_temp&styles=temp_historical_july_min&format=image%2Fpng&transparent=true&version=1.3.0&id=historical_era_july_min&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical July minimum temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=jan_min_max_mean_temp&styles=temp_historical_january_max&format=image%2Fpng&transparent=true&version=1.3.0&id=historical_era_january_max&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical January maximum temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=july_min_max_mean_temp&styles=temp_historical_july_max&format=image%2Fpng&transparent=true&version=1.3.0&id=historical_era_july_max&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Historical July maximum temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=jan_min_max_mean_temp&styles=temp_midcentury_january_min&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_january_min&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,201767",
            "text": "Projected January minimum temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=july_min_max_mean_temp&styles=temp_midcentury_july_min&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_july_min&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,201767",
            "text": "Projected July minimum temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=jan_min_max_mean_temp&styles=temp_midcentury_january_max&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_january_max&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,201767",
            "text": "Projected January maximum temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=july_min_max_mean_temp&styles=temp_midcentury_july_max&format=image%2Fpng&transparent=true&version=1.3.0&id=midcentury_era_july_max&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected July maximum temperature map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=design_freezing_index&styles=arctic_eds&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_design_freezing_index&dim_model=2&dim_era=2&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected design freezing index map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=design_thawing_index&styles=arctic_eds&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_design_thawing_index&dim_model=2&dim_era=2&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected design thawing index map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=freezing_index&styles=arctic_eds_freezing_index_future_condensed&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_freezing_index_midcentury&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected freezing index map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=thawing_index&styles=arctic_eds_thawing_index_future_condensed_compressed&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_thawing_index_midcentury&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected thawing index map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=heating_degree_days&styles=arctic_eds_heating_degree_days_future_condensed_compressed&format=image%2Fpng&transparent=true&version=1.3.0&id=ncarccsm4_heating_degree_days&dim_model=2&dim_era=2&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Projected heating degree days map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=permafrost_beta%3Aobu_pf_extent&styles=&format=image%2Fpng&transparent=true&version=1.3.0&id=pfextent_obu&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Permafrost extent (Obu) map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=iem_gipl_magt_alt_4km&styles=arctic_eds_MAGT&format=image%2Fpng&transparent=true&version=1.3.0&id=iem_gipl_magt_alt_4km_historical&dim_model=0&dim_scenario=0&dim_era=0&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Mean annual ground temperature (1986-2005) map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://zeus.snap.uaf.edu/rasdaman/ows?service=WMS&request=GetMap&layers=iem_gipl_magt_alt_4km&styles=arctic_eds_MAGT&format=image%2Fpng&transparent=true&version=1.3.0&id=iem_gipl_magt_alt_4km_2036_2065&dim_model=5&dim_scenario=2&dim_era=2&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Mean annual ground temperature (2036-2065) map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=obu_2018_magt&styles=ground_temperature_blue_to_red_arctic_eds&format=image%2Fpng&transparent=true&version=1.3.0&id=obumagt&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Mean annual ground temperature at top map layer accessible."
        },
        {
            "column": "webapp",
            "type": "url",
            "url": "https://gs.mapventure.org/geoserver/wms?service=WMS&request=GetMap&layers=permafrost_beta%3Ajorgenson_2008_pf_extent_ground_ice_volume&styles=permafrost_beta%3Aground_ice_volume&format=image%2Fpng&transparent=true&version=1.3.0&id=icevol_jorgenson&width=256&height=256&crs=EPSG%3A3338&bbox=70586,1493385,594874,2017673",
            "text": "Ground ice volume map layer accessible."
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
            "type": "javascript",
            "url": "https://arcticeds.org/engineering/design-freezing-index",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Design freezing index map loaded."
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
            "type": "javascript",
            "url": "https://arcticeds.org/engineering/freezing-index",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Freezing index map loaded."
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
            "type": "javascript",
            "url": "https://arcticeds.org/engineering/heating-degree-days",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Heating degree days map loaded."
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
    ],
}

def javascriptTest(check):
    try:
        driver.get(check["url"])
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
