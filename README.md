# Xymon Tests

This repo containes a Python script that implements custom Xymon tests for SNAP web apps. These include tests to check the validity of CSV and JSON output, as well as JavaScript tests that run in a headless web browser to check for the presence of elements in the DOM.

# Setup

Clone this repo into `/opt/xymon/server/ext`. Then, to integrate the custom test script into the Xymon configuration, add this to Xymon's `tasks.cfg` file:

```
[snap]
    ENVFILE /opt/xymon/server/etc/xymonserver.cfg
    NEEDS xymond
    CMD /opt/xymon/server/ext/snap.py
    LOGFILE $XYMONSERVERLOGS/snap.log
    INTERVAL 20m
```

This will run the full suite of tests every 20 minutes.

# Tests

Tests are grouped together by the domain name of the server. For example:

```
"example.org": [
    {
        "column": ...,
        "type": ...,
        "url": ...,
        "text": ...,
        "javascript": ...,
        "lat_range": ...,
        "lon_range": ...,
        "click": ...,
        "delay": ...
    },
]
```

The dictionary keys for each test are described in the following table:

| Key         | Required                        | Description                                                       |
| ----------- | ------------------------------- | ----------------------------------------------------------------- |
| column      | Yes                             | The column in which this test will appear on the Xymon dashboard. |
| type        | Yes                             | The type of this test. Options are javascript, csv, or json       |
| url         | Yes                             | The URL to test.                                                  |
| text        | Yes                             | A brief description of the test to be display on Xymon's test details page. |
| javascript  | Yes, if `type` is set to javascript | If this is a JavaScript test, the chunk of JavaScript code to run. The chunk of JavaScript needs to return a boolean value. |
| lat_range   | No                              | If set, choose a random latitude between the range provided. This will replace `{lat}` in the `url` and `text` values.      |
| lon_range   | No                              | If set, choose a random longitude between the range provided. This will replace `{lon}` in the `url` and `text` values. |
| click       | No                              | Selector of a DOM element to click before running a JavaScript test. |
| delay       | No                              | Override the default number of seconds to wait between loading the page and performing a JavaScript test. |

## Writing JavaScript tests

As described in the table above, you must provide a chunk of JavaScript code for any test of type `javascript`. This chunk of JavaScript code must return a boolean value. For example, here's a chunk of JavaScript that is used to count the number of legend items in a Plotly legend, and returns true if there are over 5 items in the legend (and false otherwise):

```
return document.querySelectorAll('#temp-chart .legend .traces').length > 5
```

You can run this same chunk of JavaScript code in your browser's console. Simply remove the `return` statement at the beginning, and run this in your browser console:

```
document.querySelectorAll('#temp-chart .legend .traces').length > 5
```

This means you can use your browser's console to develop new tests. Just make sure to add `return` to the beginning of the chunk of JavaScript when adding it to `snap.py`, as this is needed to return the result from Selenium's web driver.