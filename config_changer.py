from guizero import App, Text, PushButton, TextBox, Slider, Combo
from gpiozero import CPUTemperature
from time import sleep
import time
import RPi.GPIO as GPIO
import os, subprocess
import signal
from configparser import ConfigParser

#Get the configparser object
config_object = ConfigParser()

#Assume we need 2 sections in the config file, let's call them USERINFO and SERVERCONFIG
config_object["PARKINGINFO"] = {
    "parking_name": "",
    "parking_size": 0,
    "datasource": "",
    "db_name": "",
    "collection_name": "",
    "contact_number": 0,
    "contact_0": 0,
    "contact_1": 0,
    "contact_2": 0,
    "relay_number": 0,
    "relay_0": 0,
    "relay_1": 0,
    "ip": "",
    "port": 0,
    "type": ""
}

#Variable zarlah heseg
user = "PARKINGINFO"

Contact = [0,0,0]

#GPIO set hiih heseg
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def get_info_config(user, data_name, file_path='config.ini'):
    config_object.read(file_path)
    temp_data = config_object.get(user, data_name)
    print(temp_data)
    return temp_data

#Get the config_info
#def get_info_config(user, data_name):
    #userinfo = config_object[user]
    #print("{data} is {}".format(userinfo[data_name], data=data_name))
    #return userinfo[data_name]

#Write to config
def write_info_config(user, config_object):
    with open('config.ini', 'w') as conf:
        config_object.write(conf)
    
#Heregtei functionuud
def close_gui():
    sys.exit()
    
def sensor1():
    print("ok")
    
def sensor2():
    print("ok")
    
def sensor3():
    print("ok")
             
def change_info(object_name, changing_name, change_data):
    temp_data = config_object[user]
    temp_data_2 = temp_data[changing_name]
    print(temp_data_2)
    temp_data[changing_name] = change_data
    print(temp_data[changing_name])
    return "ok"

def get_change():
    temp_data = get_info_config(user, 'parking_name')
    parking_name_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'parking_size')
    parking_size_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'datasource')
    datasource_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'db_name')
    db_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'collection_name')
    coll_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'contact_number')
    con_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'contact_0')
    con1_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'contact_1')
    con2_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'contact_2')
    con3_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'relay_number')
    rel_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'relay_0')
    rel1_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'relay_1')
    rel2_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'ip')
    ip_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'port')
    port_box.value = temp_data
    print(temp_data)
    temp_data = get_info_config(user, 'type')
    type_box.value = temp_data
    print(temp_data)
    
def value_change():
    temp_data = change_info(config_object, 'parking_name', parking_name_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'parking_size', parking_size_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'datasource', datasource_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'db_name', db_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'collection_name', coll_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'contact_number', con_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'contact_0', con1_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'contact_1', con2_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'contact_2', con3_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'relay_number', rel_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'relay_0', rel1_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'relay_1', rel2_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'ip', ip_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'port', port_box.value)
    print(temp_data)
    temp_data = change_info(config_object, 'type', type_box.value)
    print(temp_data)
    write_info_config(user, config_object)
                
#App bolgon interface uusgej bga heseg  
app = App(title="Self Smart Parking", height=500, width=600, layout="grid")

welcome_message = Text(app, text="Configuration", grid=[0,0], size=40, font="Times New Roman", color="black")
name_description = Text(app, text="Which parking?", grid=[0,1], align="left")
parking_name_box = Combo(app, options=["orgil", "encanto", "central"], grid=[1,1], align="left")
size_description = Text(app, text="How many parking?", grid=[0,2], align="left")
parking_size_box = TextBox(app, grid=[1,2], align="left")
datasource_description = Text(app, text="Datasource name?", grid=[0,3], align="left")
datasource_box = Combo(app, options=["ParkingServer", "OrgilServer", "CentralServer"], grid=[1,3], align="left")
db_description = Text(app, text="Database name?", grid=[0,4], align="left")
db_box = TextBox(app, grid=[1,4], align="left")
coll_description = Text(app, text="Database username?", grid=[0,5], align="left")
coll_box = Combo(app, options=["user", "admin", "inspector"], grid=[1,5], align="left")
con_description = Text(app, text="Number of contacts using?", grid=[0,6], align="left")
con_box = Combo(app, options=["2", "3"], grid=[1,6], align="left")
con1_description = Text(app, text="Contact[1] pin?", grid=[0,7], align="left")
con1_box = Combo(app, options=["18", "23", "24", "25", "8", "7", "12", "None"], grid=[1,7], align="left")
con2_description = Text(app, text="Contact[2] pin?", grid=[0,8], align="left")
con2_box = Combo(app, options=["18", "23", "24", "25", "8", "7", "12", "None"], grid=[1,8], align="left")
con3_description = Text(app, text="Contact[3] pin?", grid=[0,9], align="left")
con3_box = Combo(app, options=["18", "23", "24", "25", "8", "7", "12", "None"], grid=[1,9], align="left")
con_description = Text(app, text="Number of relays using?", grid=[0,10], align="left")
rel_box = Combo(app, options=["2", "None"], grid=[1,10], align="left")
rel1_description = Text(app, text="Relay[1] pin?", grid=[0,11], align="left")
rel1_box = Combo(app, options=["5", "6", "None"], grid=[1,11], align="left")
rel2_description = Text(app, text="Relay[2] pin?", grid=[0,12], align="left")
rel2_box = Combo(app, options=["5", "6", "None"], grid=[1,12], align="left")
ip_description = Text(app, text="Server IP?", grid=[0,13], align="left")
ip_box = TextBox(app, grid=[1,13], align="left", width=20)
port_description = Text(app, text="Server PORT?", grid=[0,14], align="left")
port_box = TextBox(app, grid=[1,14], align="left")
type_description = Text(app, text="Barrier TYPE?", grid=[0,15], align="left")
type_box = Combo(app, options=["in", "out"], grid=[1,15], align="left")
get_text = PushButton(app, command=get_change, text="Get", grid=[1,16], align="left")
update_text = PushButton(app, command=value_change, text="Update", grid=[2,16], align="left")
app.display()