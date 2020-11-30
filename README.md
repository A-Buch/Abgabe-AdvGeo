# Abgabe-AdvGeo
 
## Introduction 
The aim of this project is to visualize a predicted contamination of Particulate Matter (PM) with a size smaller than 2.5 µg/m³. The study area is primiary the city center of Stuttgart between the 1st October and 1st November 2020. 
Several free of charge data sources were used to calculate if a strong or low contamination through PM 2.5, so the local PM concentration was obtained from stations for air quality, conducted by the luftdaten community. Meteorological data were obtained via the API from the german weather forecast (DWD).
The result are less meaningful due to the fact that the main feature, the traffic volume, is not included in the following calcualtions. It is quite difficult to receive free of charge data about the traffic volume, especially for a certain location. 
Also the spatial and temporal autocorrelation of PM is disregared. But still the visualizion gives an impression of the predicted results.

## Setup
To run the script of the finalproject.ipynb you need to install several packages, if they are not already existing in your current environment. The packages can be install via [pip](https://pip.pypa.io/en/stable/) or [conda](https://docs.conda.io/projects/conda/en/latest/).
Example via pip:
```bash
pip install wetterdienst # API from the german weatherforecast 
pip install -U scikit-learn # machine learning
pip install dash==1.17.0  # visualization 
pip install plotly==4.13.0 #  visualization
pip install pdb # degugging
pip install -U pytest # testing package 
```

## Getting started
Run the finalproject.ipynb in jupter notebook in a virtual environemnt (e.g advgeo37) and open the Dashboard on (http://127.0.0.1:8050/). To discover how the predicted Particulate Matter concentration changes over time, you can adapt the number of the stations in the Dashboard and rerun the algorithm.
The Dashboard is inspired by an example from dash and is about a Support Vector Classifier. Its code can be accessed via [github](https://github.com/plotly/dash-svm/tree/0206da7d7d3247fa4a2c600563720f061b58aeb0).
If you want to test this dash sample external, you can do this e.g. via cloning this [repository](https://github.com/plotly/dash-sample-apps.git).
Navigate to the root of the repository on your computer, run the app.py file with following command in your cmd and then visit (http://127.0.0.1:8050/) in your web browser.
```bash
python apps/dash-svm/app.py
```

The stylesheet (CSS file) is accessed from the webpage of Codepen.
Template Stylesheet: https://codepen.io/chriddyp/
A test file (test_utils_finalproject.py) was created to check if the own created functions in the module "utils/utils_finalproject.py" work properly.
The tests are run by the testing framework [Pytest](https://docs.pytest.org/en/stable/contents.html). Pytest overs detailed information on failed assert statements 
and can be run in the cmd.
```bash
pytest utils/test_utils_finalproject.py 
```

The station data for air quality was accessed from the archive of the luftdaten sensor community, a citizen science programme. 
[Wget](https://www.gnu.org/software/wget/) was used in the console with following command to receive selected sensor data, eg. from a station with the id 14356:
```bash
 wget -r -l3 -np -P "./data" --accept-regex="2020-1[0-1]*-[0-9][0-9]*" -A "_14356.csv" -X "2015*,2016*,2017*,2018*,2019*"  http://archive.sensor.community/
```


#### Have fun !
