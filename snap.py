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
            "test": """
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
            "test": "return document.querySelectorAll('#precip-chart .legend .traces').length > 5",
            "text": "Temperature chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "test": """
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
            "test": "return document.querySelectorAll('#precip-chart .legend .traces').length > 5",
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
        },
    ],
    "production-fire-tally.us-west-2.elasticbeanstalk.com": [
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "test": "return document.querySelectorAll('#tally .legendlines').length > 5",
            "text": "Statewide daily tally chart is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "test": "return document.querySelectorAll('#tally-zone .legendlines').length > 5",
            "text": "Daily tally by protection chart graph is populated."
        },
        {
            "column": "webapp",
            "type": "javascript",
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "test": "return document.querySelectorAll('#tally-year .legendlines').length > 5",
            "text": "Daily tally by year chart is populated."
        },
    ]
}

def javascriptCheck(check):
    try:
        driver.get(check["url"])
        time.sleep(10)
        return driver.execute_script(check["test"])
    except:
        return False


def csvCheck(check):
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


def jsonCheck(check):
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
            success = javascriptCheck(check)
        elif check["type"] == "json":
            success = jsonCheck(check)
        elif check["type"] == "csv":
            success = csvCheck(check)

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
