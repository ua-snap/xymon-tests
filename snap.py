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

pass_icon = '<img src="/xymon/gifs/green.gif" alt="green" height="16" width="16" border="0">'
fail_icon = '<img src="/xymon/gifs/red.gif" alt="green" height="16" width="16" border="0">'

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
            "type": "javascript",
            "url": "https://arcticeds.org/climate/snowfall",
            "javascript": "return document.querySelectorAll('#map .leaflet-tile-loaded').length > 20",
            "text": "Snowfall map loaded."
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

        if success == True:
            messages[column] += pass_icon + " " + check["text"] + "\n"
        else:
            colors[column] = "red"
            messages[column] += fail_icon + " " + check["text"] + "\n"

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
