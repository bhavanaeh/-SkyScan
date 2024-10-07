from shiny import App, ui, render,reactive
from shinywidgets import output_widget, render_widget
from ipyleaflet import Map, Polyline, basemaps, FullScreenControl, Marker
import requests
import pandas as pd
from pandas import read_csv
from ipyleaflet import Map, Marker, MarkerCluster
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import HTML
from time import sleep
import datetime
from datetime import datetime, timedelta
import time
import json
import faicons


df_airports = pd.read_csv('data/us-airports.csv')
airport_list = df_airports["name"].tolist()

list_of_airlines = ['Alaska Airlines Inc','American Airlines Inc', 'American Eagle Airlines Inc','Atlantic Southeast Airlines','Delta Air Lines Inc','Frontier Airlines Inc','Hawaiian Airlines Inc','JetBlue Airways','SkyWest Airlines Inc','Southwest Airlines Co','Spirit Air Lines','United Air Lines Inc','Virgin America','US Airways Inc']

df_aircrafts = pd.read_csv('data/aircrafts-info.csv')

# Filter the DataFrame
df_aircrafts = df_aircrafts[df_aircrafts['registration'].str.startswith('N') & df_aircrafts['owner'].isin(list_of_airlines)]
df_aircrafts = df_aircrafts.dropna(subset=['registration'])

def fetch_icao24():
    url = "https://opensky-network.org/api/states/all"
    params = {
            "lamin": 24.396308,  # Latitude min (bottom)
            "lomin": -125.0,      # Longitude min (left)
            "lamax": 49.5904,   # Latitude max (top)
            "lomax": -66.93457    # Longitude max (right)
        }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        flights = []
        for aircraft in data["states"]:
            if aircraft[2] is not None and aircraft[5] is not None:
                flights.append({"icao24": aircraft[0]})
        df = pd.DataFrame(flights)
        icao24 = df['icao24'].tolist()
        icao24.append("")
        return icao24

def nav_controls():
    return [
        ui.nav_panel("Flight Tracker", 
                    ui.input_selectize("icao24", "Select Aircraft", choices=fetch_icao24(), selected=""),
                    output_widget("mark_us_flights"),
                    ui.hr(),
                    ui.panel_conditional("input.radio === 'Departures'", ui.output_data_frame("display_departures_by_airport")),
                    ui.panel_conditional("input.radio === 'Arrivals'", ui.output_data_frame("display_arrials_by_airport")),),
        ui.nav_panel("Aircraft Explorer", 
                    ui.layout_columns(
                        ui.input_selectize("lookupicao24", "Look Up ICAO24", choices=fetch_icao24(), selected=""), 
                        ui.input_selectize("aircraft", "Look Up Registration Number", choices=df_aircrafts['registration'].tolist(), multiple=True),
                        ui.input_selectize("airline", "Look Up Airline", choices=list_of_airlines, multiple=True),),
                    ui.output_data_frame("display_aircraft_data")),
        ui.nav_panel("About", ui.markdown("""
## SkyScan (USA)

SkyScan is an interactive web application that provides real-time information about airborne aircrafts over the United States.
This webapp also allows users to track flights (view flight paths), explore and download detailed information about specific US aircrafts! 

**Goal of the WebApp:**

Despite the availability of a variety of flight tracking solutions, there are still challenges related to the integration of real-time data feeds and user-friendly access to this data.
This web-app is primarily designed for aviation enthusiasts (like me!) who enjoy tracking flights and studying trends, thereby proving to be a user-friendly and interactive tool aimed at facilitating easy exploration and collection of aviation data in an intuitive way.
                                          
**How to use SkyScan:**

1. **Flight Tracker:**
    - The map displays the current location of all airborne aircrafts over the United States. Click on a marker to view detailed information about a specific aircraft.
    - Select an aircraft (ICAO24 Code) from the dropdown menu to view its current location and flight path. The ICAO24 code is an unique identifier for aircrafts. This information can either be found by hovering over the aircraft marker on the map or by navigating to the 'Aircraft Explorer' tab.
    - Use the 'Departures' and 'Arrivals' tabs to view **historic** information about US flights departing from or arriving at a specific airport on a given date and time range (limited to 24 hours to ensure optimal performance).
    - The table displays detailed information about the selected flights, including their ICAO24 code, callsign, first seen, departure airport, last seen, and arrival airport and can be downloaded as a CSV file by clicking the 'Download Data' button.

2. **Aircraft Explorer:**
    - This tab allows users to explore detailed information about a particular US aircraft. Users can filter aircrafts by their ICAO24 code, Registration Number(s), and Commercial Airline(s). 
    - The table displays detailed information about the selected aircrafts, including their registration, manufacturer, model, engine and owner. 
    - A limitation to note is that the data is limited to aircrafts registered in the United States and owned by only a select list of commercial airlines (Top 10).
                                                                                    
**How to run the code:**
The web app is built primarily using the Shiny library in Python and extensively leverages the [OpenSky Network API] (https://openskynetwork.github.io/opensky-api/rest.html), thus it would be ideal to familirize yourself with the API and its limitations before running the code. To run the code, the first step is to have Python 3.11 installed on your system. You can directly download and install Python from [python.org](https://www.python.org/).
Once you have Python installed, you can run the code by executing the following commands in your terminal:
 ```
python3.11 -m pip install uv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
shiny run --reload --launch-browser ./app.py
```
                                        
Developed as a part of the coursework (Final Project) for [CS 498 : End to End Data Science](https://daviddalpiaz.github.io/cs498-sp24/final-project.html) at the University of Illinois Urbana-Champaign by Bhavana Sundar (bsundar3)
""")),
        ui.nav_spacer(),
    ]

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.value_box(title="Airborne Aircrafts", showcase= faicons.icon_svg("plane", width="50px"), 
                    value=ui.output_ui("airborne_aircrafts_ct"),
                    theme="bg-gradient-blue-purple", height="200px"), 
        ui.hr(),
        ui.input_radio_buttons("radio", "Get Flights By ", ["Departures", "Arrivals"]),
    ui.panel_conditional(
        "input.radio === 'Departures'",
        (ui.input_date("date1", "Departure Date", value="2021-01-01"),
        ui.input_slider("slider1", "Departure Time Range (Hours)", 1,24, [15,20], step=1),
        ui.input_selectize("airport1", "Departure Airport",choices=airport_list,selected="Chicago O'Hare International Airport"),),

    ),
    ui.panel_conditional(
        "input.radio === 'Arrivals'",
        (ui.input_date("date2", "Arrival Date", value="2021-01-01"),
        ui.input_slider("slider2", "Arrival Time Range (Hours)", 1,24, [15,20], step=1),
        ui.input_selectize("airport2", "Arrival Airport",choices=airport_list,selected="Los Angeles International Airport"),),

    ),
    ui.download_button("download", "Download Data (CSV)"),
    width="280px"),
        ui.div(
            ui.page_navbar(
                *nav_controls(),
                id="navbar_id",
                header=ui.div(
                    {"style": "width:576; margin: 0 auto"},
                ui.tags.style(
                    """
                    h4 {
                        margin-top: 3em;
                    }
                    """
                ),
            ),
            ),
        ),
        title="SkyScan (USA)",
    )


def server(input, output, session):

    @render.data_frame
    def display_arrials_by_airport():
        df = get_arrivals_by_airport()
        return render.DataGrid(df,width="100%")
    
    @render.data_frame
    def display_departures_by_airport():
        df = get_departures_by_airport()
        return render.DataGrid(df,width="100%")


    def get_arrivals_by_airport():
        
        date_format = "%Y-%m-%d"
        d = str(input.date2())
        date = datetime.strptime(d, date_format)
        print(date)
        unix_time = int(time.mktime(date.timetuple())) - (6 * 3600)  # Subtract 6 hours to account for timezone difference

        start = input.slider2()[0]
        end = input.slider2()[1]

        
        ident = df_airports[df_airports['name'] == input.airport2()]['ident'].values[0]
        url = "https://opensky-network.org/api/flights/arrival"
        params = {
            "airport": ident,
            "begin": unix_time + (start * 3600),  
            "end": unix_time + (end * 3600)
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df = df[['icao24', 'callsign', 'firstSeen', 'estDepartureAirport', 'lastSeen', 'estArrivalAirport']]
            df['firstSeen'] = df['firstSeen'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
            df['lastSeen'] = df['lastSeen'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
            df = df.rename(columns={'icao24': 'ICAO24', 'callsign': 'Call Sign', 'firstSeen': 'First Seen', 'estDepartureAirport': 'Departure Airport', 'lastSeen': 'Last Seen', 'estArrivalAirport': 'Arrival Airport'})
            airport_code_to_name = df_airports.set_index('ident')['name'].to_dict()
            df['Departure Airport'] = df['Departure Airport'].map(airport_code_to_name)
            df['Arrival Airport'] = df['Arrival Airport'].map(airport_code_to_name)
            return df
        else:
            print("Error fetching data:", response.status_code)

    
    def get_departures_by_airport():

        date_format = "%Y-%m-%d"
        d = str(input.date1())
        date = datetime.strptime(d, date_format)
        unix_time = int(time.mktime(date.timetuple())) - (6 * 3600)  # Subtract 6 hours to account for timezone difference


        start = input.slider1()[0]
        end = input.slider1()[1]

        
        ident = df_airports[df_airports['name'] == input.airport1()]['ident'].values[0]
        url = "https://opensky-network.org/api/flights/departure"
        params = {
            "airport": ident,
            "begin": unix_time + (start * 3600), 
            "end": unix_time + (end * 3600) 
        }

        response = requests.get(url, params=params)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df = df[['icao24', 'callsign', 'firstSeen', 'estDepartureAirport', 'lastSeen', 'estArrivalAirport']]
            df['firstSeen'] = df['firstSeen'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
            df['lastSeen'] = df['lastSeen'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
            df = df.rename(columns={'icao24': 'ICAO24', 'callsign': 'Call Sign', 'firstSeen': 'First Seen', 'estDepartureAirport': 'Departure Airport', 'lastSeen': 'Last Seen', 'estArrivalAirport': 'Arrival Airport'})
            airport_code_to_name = df_airports.set_index('ident')['name'].to_dict()
            df['Departure Airport'] = df['Departure Airport'].map(airport_code_to_name)
            df['Arrival Airport'] = df['Arrival Airport'].map(airport_code_to_name)
            df = pd.DataFrame(df)
            return df
        else:
            print("Error fetching data:", response.status_code)

    def get_all_us_flights():

        url = "https://opensky-network.org/api/states/all"
        params = {
            "lamin": 24.396308,  # Latitude min (bottom)
            "lomin": -125.0,      # Longitude min (left)
            "lamax": 49.5904,   # Latitude max (top)
            "lomax": -66.93457    # Longitude max (right)
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            flights = []
            for aircraft in data["states"]:
                if aircraft[2] is not None and aircraft[5] is not None:
                    flights.append({
                        "icao24": aircraft[0],
                        "callsign": aircraft[1],
                        "latitude": aircraft[6],
                        "longitude": aircraft[5],
                        "altitude": aircraft[7],
                        "velocity": aircraft[9],
                        "vertical_rate": aircraft[11],
                        "heading": aircraft[10],
                        "origin_country": aircraft[2]
                    })
            df = pd.DataFrame(flights)
            return df
        else:
            print("Error fetching data:", response.status_code)

    all_us_flights = get_all_us_flights()

    @render.text
    def airborne_aircrafts_ct():
        ct = len(all_us_flights)
        return ct
    
    @render_widget
    def mark_us_flights():
        print(input.icao24())
        if input.icao24() == "":
            map_center = [39.8283, -98.5795]
            m = Map(center=map_center, zoom=3.5)
            markers = []
            for index, row in all_us_flights.iterrows():
                marker = Marker(location=(row['latitude'], row['longitude']), title=f"ICAO24: {row['icao24']}, Callsign: {row['callsign']}, Altitude: {row['altitude']}, Velocity: {row['velocity']}, Vertical Rate: {row['vertical_rate']}, Heading: {row['heading']}, Origin Country: {row['origin_country']}")
                markers.append(marker)
            marker_cluster = MarkerCluster(markers=markers)
            m.add_layer(marker_cluster)
            m.zoom_control = False

            return m
        else:
            icao24 = input.icao24()
            url = f"https://opensky-network.org/api/tracks/all?icao24={icao24}"
            url = url = f"https://opensky-network.org/api/tracks/all?icao24={icao24}"
            response = requests.get(url)

            if response.status_code == 200:
                data = json.loads(response.text)
                m = Map(center=(data["path"][0][1], data["path"][0][2]), zoom=10)
                flight_path = [(point[1], point[2]) for point in data["path"]]
                flight_path_line = Polyline(locations=flight_path, color="black", fill=False, dash_array="10 10")
                m.add_layer(flight_path_line)
                start_marker = Marker(location=flight_path[0], draggable=False) # started from - departure
                end_marker = Marker(location=flight_path[-1], draggable=False) # current location
                unix_time = data['startTime']
                datetime_obj_utc = datetime.utcfromtimestamp(unix_time)
                datetime_obj_local = datetime_obj_utc - timedelta(hours=6)
                start_popup = HTML(value=f"ICAO24: {icao24} <br>Call Sign: {data['callsign']} <br>Departure Time: {datetime_obj_local}")                                  
                start_marker.popup = start_popup
                m.add_layer(start_marker)                    
                return m

    @render.data_frame
    def display_aircraft_data():
        df = get_aircraft_data()
        return df

    def get_aircraft_data():
        if input.aircraft() == () and input.airline() == () and input.lookupicao24() == "":
            df = df_aircrafts
            df = df.drop(columns=['linenumber','operatoriata' ,'testreg','registered', 'status','modes','adsb','acars','notes','categoryDescription'])
            df = df.rename(columns={'icao24': 'ICAO24','registration': 'Registration Number', 'manufacturericao': 'Manufacturer ICAO', 'manufacturername': 'Manufacturer Name', 'model': 'Model','typecode':'Type Code','serialnumber':'Serial Number','icaoaircrafttype':'ICAO Aircraft Type','operator': 'Operator','operatorcallsign':'Operator Call Sign', 'reguntil': 'Registration Valid Until', 'built': 'Built', 'firstflightdate': 'First Flight Date', 'seatconfiguration': 'Seat Configuration', 'engines': 'Engines'})
            return df
        elif input.aircraft() != () and input.airline() == () and input.lookupicao24() == "":
            df_filtered = df_aircrafts[df_aircrafts['registration'].isin(input.aircraft())]
            df = df_filtered
            df = df.drop(columns=['linenumber','operatoriata' ,'testreg','registered', 'status','modes','adsb','acars','notes','categoryDescription'])
            df = df.rename(columns={'icao24': 'ICAO24','registration': 'Registration Number', 'manufacturericao': 'Manufacturer ICAO', 'manufacturername': 'Manufacturer Name', 'model': 'Model','typecode':'Type Code','serialnumber':'Serial Number','icaoaircrafttype':'ICAO Aircraft Type','operator': 'Operator','operatorcallsign':'Operator Call Sign', 'reguntil': 'Registration Valid Until', 'built': 'Built', 'firstflightdate': 'First Flight Date', 'seatconfiguration': 'Seat Configuration', 'engines': 'Engines'})
            return df
        elif input.aircraft() == () and input.airline() != () and input.lookupicao24() == "":
            df_filtered = df_aircrafts[df_aircrafts['owner'].isin(input.airline())]
            df = df_filtered
            df = df.drop(columns=['linenumber','operatoriata' ,'testreg','registered', 'status','modes','adsb','acars','notes','categoryDescription'])
            df = df.rename(columns={'icao24': 'ICAO24','registration': 'Registration Number', 'manufacturericao': 'Manufacturer ICAO', 'manufacturername': 'Manufacturer Name', 'model': 'Model','typecode':'Type Code','serialnumber':'Serial Number','icaoaircrafttype':'ICAO Aircraft Type','operator': 'Operator','operatorcallsign':'Operator Call Sign', 'reguntil': 'Registration Valid Until', 'built': 'Built', 'firstflightdate': 'First Flight Date', 'seatconfiguration': 'Seat Configuration', 'engines': 'Engines'})
            return df
        elif input.aircraft() != () and input.airline()!= () and input.lookupicao24() == "":
            df_filtered = df_aircrafts[df_aircrafts['registration'].isin(input.aircraft()) & df_aircrafts['owner'].isin(input.airline())]
            df = df_filtered
            df = df.drop(columns=['linenumber','operatoriata' ,'testreg','registered', 'status','modes','adsb','acars','notes','categoryDescription'])
            df = df.rename(columns={'icao24': 'ICAO24','registration': 'Registration Number', 'manufacturericao': 'Manufacturer ICAO', 'manufacturername': 'Manufacturer Name', 'model': 'Model','typecode':'Type Code','serialnumber':'Serial Number','icaoaircrafttype':'ICAO Aircraft Type','operator': 'Operator','operatorcallsign':'Operator Call Sign', 'reguntil': 'Registration Valid Until', 'built': 'Built', 'firstflightdate': 'First Flight Date', 'seatconfiguration': 'Seat Configuration', 'engines': 'Engines'})
            return df
        elif input.lookupicao24() != "" and input.aircraft() == () and input.airline() == ():
            df_filtered = df_aircrafts[df_aircrafts['icao24'] == input.lookupicao24()]
            df = df_filtered
            df = df.drop(columns=['linenumber','operatoriata' ,'testreg','registered', 'status','modes','adsb','acars','notes','categoryDescription'])
            df = df.rename(columns={'icao24': 'ICAO24','registration': 'Registration Number', 'manufacturericao': 'Manufacturer ICAO', 'manufacturername': 'Manufacturer Name', 'model': 'Model','typecode':'Type Code','serialnumber':'Serial Number','icaoaircrafttype':'ICAO Aircraft Type','operator': 'Operator','operatorcallsign':'Operator Call Sign', 'reguntil': 'Registration Valid Until', 'built': 'Built', 'firstflightdate': 'First Flight Date', 'seatconfiguration': 'Seat Configuration', 'engines': 'Engines'})
            return df
        elif input.lookupicao24() != "" and input.aircraft() != () and input.airline() == ():
            df_filtered = df_aircrafts[df_aircrafts['icao24'] == input.lookupicao24() & df_aircrafts['registration'].isin(input.aircraft())]
            df = df_filtered
            df = df.drop(columns=['linenumber','operatoriata' ,'testreg','registered', 'status','modes','adsb','acars','notes','categoryDescription'])
            df = df.rename(columns={'icao24': 'ICAO24','registration': 'Registration Number', 'manufacturericao': 'Manufacturer ICAO', 'manufacturername': 'Manufacturer Name', 'model': 'Model','typecode':'Type Code','serialnumber':'Serial Number','icaoaircrafttype':'ICAO Aircraft Type','operator': 'Operator','operatorcallsign':'Operator Call Sign', 'reguntil': 'Registration Valid Until', 'built': 'Built', 'firstflightdate': 'First Flight Date', 'seatconfiguration': 'Seat Configuration', 'engines': 'Engines'})
            return df
        elif input.lookupicao24() != "" and input.aircraft() == () and input.airline() != ():
            df_filtered = df_aircrafts[df_aircrafts['icao24'] == input.lookupicao24() & df_aircrafts['owner'].isin(input.airline())]
            df = df_filtered
            df = df.drop(columns=['linenumber','operatoriata' ,'testreg','registered', 'status','modes','adsb','acars','notes','categoryDescription'])
            df = df.rename(columns={'icao24': 'ICAO24','registration': 'Registration Number', 'manufacturericao': 'Manufacturer ICAO', 'manufacturername': 'Manufacturer Name', 'model': 'Model','typecode':'Type Code','serialnumber':'Serial Number','icaoaircrafttype':'ICAO Aircraft Type','operator': 'Operator','operatorcallsign':'Operator Call Sign', 'reguntil': 'Registration Valid Until', 'built': 'Built', 'firstflightdate': 'First Flight Date', 'seatconfiguration': 'Seat Configuration', 'engines': 'Engines'})
            return df
        else:
            df_filtered = df_aircrafts[df_aircrafts['icao24'] == input.lookupicao24() & df_aircrafts['registration'].isin(input.aircraft()) & df_aircrafts['owner'].isin(input.airline())]
            df = df_filtered
            df = df.drop(columns=['linenumber','operatoriata' ,'testreg','registered', 'status','modes','adsb','acars','notes','categoryDescription'])
            df = df.rename(columns={'icao24': 'ICAO24','registration': 'Registration Number', 'manufacturericao': 'Manufacturer ICAO', 'manufacturername': 'Manufacturer Name', 'model': 'Model','typecode':'Type Code','serialnumber':'Serial Number','icaoaircrafttype':'ICAO Aircraft Type','operator': 'Operator','operatorcallsign':'Operator Call Sign', 'reguntil': 'Registration Valid Until', 'built': 'Built', 'firstflightdate': 'First Flight Date', 'seatconfiguration': 'Seat Configuration', 'engines': 'Engines'})
            return df

    @render.download(filename="SkyScanData.csv")
    def download():
        if input.radio() == "Departures":
            df = get_departures_by_airport()
            df.to_csv("/tmp/data.csv", index=False)
            with open("/tmp/data.csv", "r") as file:
                yield file.read()
        elif input.radio() == "Arrivals":
            df = get_arrivals_by_airport()
            df.to_csv("/tmp/data.csv", index=False)
            with open("/tmp/data.csv", "r") as file:
                yield file.read()
        else:
            #this doesnt work 
            df = get_aircraft_data()
            df.to_csv("/tmp/data.csv", index=False)
            with open("/tmp/data.csv", "r") as file:
                yield file.read()

app = App(app_ui, server=server)
    