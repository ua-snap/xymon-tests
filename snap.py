#!/usr/bin/env python
import os
import subprocess
import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

column = "javascript"

xymon = os.getenv("XYMON")
xymsrv = os.getenv("XYMSRV")

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, executable_path="/usr/bin/geckodriver", service_log_path="/tmp/geckodriver.log")

checks = {
    "northernclimatereports.org": [
        {
            "url": "https://northernclimatereports.org/report/community/AK124#results",
            "test": "return _.inRange(parseFloat(document.querySelector('.report--temperature .diff').textContent.substring(1)), 0, 10)",
            "failure": "Temperature table values are not valid."
        }
    ],
    "production-fire-tally.us-west-2.elasticbeanstalk.com": [
        {
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "test": "return document.querySelector('#tally .legendlines') != undefined",
            "failure": "Statewide daily tally graph is not populated."
        },
        {
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "test": "return document.querySelector('#tally-zone .legendlines') != undefined",
            "failure": "Daily tally by protection area graph is not populated."
        },
        {
            "url": "https://snap.uaf.edu/tools/daily-fire-tally",
            "test": "return document.querySelector('#tally-year .legendlines') != undefined",
            "failure": "Daily tally by year graph is not populated."
        },
    ]
}

for machine in checks.keys():
    color = "green"
    msg = ""
    for check in checks[machine]:
        success = True
        try:
            driver.get(check["url"])
            time.sleep(5)
            success = driver.execute_script(check["test"])
        except:
            success = False
            pass

        if not success:
            color = "red"
            msg += check["failure"] + "\n"

    if color is "green":
        msg = "All tests passed."

    date = subprocess.check_output(["date"])
    machine_safe = machine.replace(".", ",")
    status = "status {}.{} {} {}\n\n{}".format(machine, column, color, date, msg)
    subprocess.call([xymon, xymsrv, status])

driver.quit()
