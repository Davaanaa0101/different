#Sanguud duudah heseg
import RPi.GPIO as GPIO
import time
import logging
from time import strftime
from pymongo import MongoClient
import pymongo
import json
from configparser import ConfigParser
import socket

#Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

def tcp_send(ip, port, message):
    while True:
        try:
            # Create a socket and connect to the server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, port))
                
                # Send the message
                s.sendall(message.encode('utf-8'))
                
                # Receive any response (optional, depending on your use case)
                response = s.recv(1024)
                print("Received:", response.decode('utf-8'))
                
            # If the message is sent successfully, break out of the loop
            break

        except socket.error as e:
            # Handle the socket error
            print(f"Socket error: {e}")

            # Wait for some time before retrying (adjust the sleep duration as needed)
            time.sleep(5)
        
def tcp_read():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    data = s.recv(BUFFER_SIZE)
    print ("received data:", data)
    s.close()
    return data

parking_site_name = ""
parking_size = 0
parking_type = ""
#RPI holbootoi hulnuudiin daraalalaar n oruulna 1,2,3 geh met
Contact = [0, 0, 0]
Relay = [0, 0]
#Heregtei global huwisagchdiig zarlana
count = 0 #Niit zogsoold bga mashini too
in_count = 0 #Orson mashinii too
out_count = 0 #Garsan mashinii too
car_back_count = 0 #Uharsan mashinii too
sensor_count = 2 #Suuriluulsan sensoriin hemjeeg zaana
prev_value = 0 #Tuluw 1
next_value = 0 #Tuluw 2
abnormal_state = False #Aldaatai zasagdahiig huleej bui tuluw
barrier_sensor = False #Barrier neelttei eswel haalttai tuluw
notified_waiting = False
notified_car_back = False

raw_count = 0
raw_count_status = False

#print("Sensoriin tohirgoo: {sensor}".format(sensor = sensor_count))
sensor_data = [False,False,False]

#Get the password
def get_info_config():
    global parking_site_name, parking_size, parking_type, sensor_count, sensor_data, Contact, TCP_IP, TCP_PORT
    logging.info("System config reading, STARTED!")
    userinfo = config_object["PARKINGINFO"]
    parking_site_name = userinfo["parking_name"]
    logging.info("Pakring name: {}!".format(parking_site_name))
    parking_size = userinfo["parking_size"]
    logging.info("Parking size: {}!".format(parking_size))
    parking_type = userinfo["type"]
    logging.info("Parking type: {}!".format(parking_type))
    sensor_count = int(userinfo["contact_number"])
    logging.info("Sensor number: {}!".format(sensor_count))
    if sensor_count == 2:
        Contact[0] = int(userinfo["contact_0"])
        logging.info("Sensor number 1: {}!".format(Contact[0]))
        Contact[1] = int(userinfo["contact_1"])
        logging.info("Sensor number 2: {}!".format(Contact[1]))
    elif sensor_count == 3:
        Contact[0] = int(userinfo["contact_0"])
        logging.info("Sensor number 1: {}!".format(Contact[0]))
        Contact[1] = int(userinfo["contact_1"])
        logging.info("Sensor number 2: {}!".format(Contact[1]))
        Contact[2] = int(userinfo["contact_2"])
        logging.info("Sensor number 3: {}!".format(Contact[2]))
    print("Parking name is {}".format(userinfo["parking_name"]))
    TCP_IP = userinfo["ip"]
    print(TCP_IP)
    TCP_PORT = int(userinfo["port"])
    print(TCP_PORT)
    logging.info("System config reading, OK!")

# Connect to MongoDB server
client = MongoClient('mongodb://parking_in:parkingtest@ac-5c9t9sc-shard-00-00.pvgousi.mongodb.net:27017,ac-5c9t9sc-shard-00-01.pvgousi.mongodb.net:27017,ac-5c9t9sc-shard-00-02.pvgousi.mongodb.net:27017/?ssl=true&replicaSet=atlas-7h47fd-shard-0&authSource=admin&retryWrites=true&w=majority')
# Select database and collection
datasource = "ParkingServer"
db = client['parkingdata']
collection = db['user']

#Contactuud buyu medregchuudiin holbogdosn huliig zaaj ugnu /BCM/
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Logger tohirgoo
LOG_LEVEL = logging.INFO
#LOG_LEVEL = loggign.DEBUG
def get_file_date():
    return "/home/davaa/Desktop/log/mylog" + str(strftime("%m%d%Y, %H:%M:%S")) + ".txt"

name = get_file_date()
print("log file: ",name)
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=name, format=LOG_FORMAT, encoding='utf-8', level=LOG_LEVEL, filemode="w")
logging.info("System started!")



#Sensor 1-n medeelliig BOOL bolgoh heseg
def sensor1(channel):
    global sensor_data
    time.sleep(0.25)
    sensor_data[0] = bool(GPIO.input(channel))
    
#Sensor 2-n medeelliig BOOL bolgoh heseg
def sensor2(channel):
    global sensor_data
    time.sleep(0.25)
    sensor_data[1] = bool(GPIO.input(channel))
    
#Sensor 3-n medeelliig BOOL bolgoh heseg
def sensor3(channel):
    global sensor_data
    time.sleep(0.25)
    sensor_data[2] = bool(GPIO.input(channel))
    if sensor_data[2] == True:
        raw_count += 1
        raw_count_status = True
   
#Sensor 4-n medeelliig BOOL bolgoh heseg
def barrier_sense(channel):
    global barrier_sense
    time.sleep(0.25)
    sensor_data[3] = bool(GPIO.input(channel))

#Contact hulnuudiig orolt bolgoj zarlana
def sensor_init():
    if sensor_count == 3:
        for i in range(0,3):
            GPIO.setup(Contact[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)
            print("Contact: ", Contact[i])
            sensor_data[i] = bool(GPIO.input(Contact[i]))
            ##print("Contact setup, OK.")
            logging.info("Sensor check {number}, OK.".format(number = i))
        GPIO.add_event_detect(Contact[0], GPIO.BOTH, callback=sensor1, bouncetime=250)
        GPIO.add_event_detect(Contact[1], GPIO.BOTH, callback=sensor2, bouncetime=250)
        GPIO.add_event_detect(Contact[2], GPIO.BOTH, callback=sensor3, bouncetime=250)            
    elif sensor_count == 2:
        for i in range(0,2):
            GPIO.setup(Contact[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)
            logging.info("Sensor check {number}, OK.".format(number = Contact[i]))
            sensor_data[i] = bool(GPIO.input(Contact[i]))
            ##print("Contact setup, OK.")
            logging.info("Sensor check {number}, OK.".format(number = i))
        GPIO.add_event_detect(Contact[0], GPIO.BOTH, callback=sensor1, bouncetime=250)
        GPIO.add_event_detect(Contact[1], GPIO.BOTH, callback=sensor2, bouncetime=250)


#Server luu ywuulah command
def send_ok():
    return

#Server luu mashin zogsood bgag medeellene
def standing_still():
    return    

#Sensoriig shalgah ded function
def check_sensor(number_of_sensor):
    ##print("Reading sensor: ", number_of_sensor)
    ##print("Reading status: ", GPIO.input(Contact[number_of_sensor]))
    return(GPIO.input(Contact[number_of_sensor]))

#Status log hiih command  
def logging_command(logging_text):
    logging.info(logging_text)
    
#Sensoruudiin odoo bga tuluwuus hamaarch 3 orontoi too bolgoh heseg
def check_sensor_states():
    global sensor_data, barrier_sensor
    sensor_value = 0
    #print("Sensor_data:", sensor_data)
    if sensor_data == [True, True, True]:
        sensor_value = 0
    if sensor_data == [True, True, False]:
        sensor_value = 1
    if sensor_data == [True, False, True]:
        sensor_value = 10
    if sensor_data == [True, False, False]:
        sensor_value = 11
    if sensor_data == [False, True, True]:
        sensor_value = 100
    if sensor_data == [False, True, False]:
        sensor_value = 101
    if sensor_data == [False, False, True]:
        sensor_value = 110
    if sensor_data == [False, False, False]:
        sensor_value = 111
    return sensor_value

#Sensoruudiin odoo bga tuluwuus hamaarch 2 orontoi too bolgoh heseg
def check_sensor_states_two():
    global sensor_data, barrier_sensor
    sensor_value = 0
    if sensor_data == [True, True, False]:
        sensor_value = 0
    if sensor_data == [True, False, False]:
        sensor_value = 1
    if sensor_data == [False, True, False]:
        sensor_value = 10
    if sensor_data == [False, False, False]:
        sensor_value = 11
    return sensor_value
    
#Abnormal state orson tohioldold dotroo shalgah uildel hiij zasagdsan tohioldold garah ded function
def abnormal_state_recover(abnormal_value):
    global next_value, sensor_count, prev_value
    global abnormal_state, parking_type
    if parking_type == "in":
        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": abnormal_value}})     
        update_one({"name": parking_site_name}, {"$set": {"in_abnormal_last_state_text": abnormal_value}})           
        update_one({"name": parking_site_name}, {"$set": {"in_abnormal_last_state_time": str(strftime("%m%d%Y, %H:%M:%S"))}})
    elif parking_type == "out":
        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": abnormal_value}})               
        update_one({"name": parking_site_name}, {"$set": {"out_abnormal_last_state_text": abnormal_value}})
        update_one({"name": parking_site_name}, {"$set": {"out_abnormal_last_state_time": str(strftime("%m%d%Y, %H:%M:%S"))}})
    get_data(parking_site_name)
    while abnormal_state == True:
        if abnormal_value == 0:
            if sensor_count == 2:
                next_value = check_sensor_states_two()
                if next_value == 0:
                    abnormal_state = False
                    #print("Abnormal case recovered!")
                    logging_command("Abnormal case recovered!")
                    if parking_type == "in":
                        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": 0}})
                    elif parking_type == "out":
                        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": 0}})
            elif sensor_count == 3:
                next_value = check_sensor_states()
                if next_value == 0:
                    abnormal_state = False
                    #print("Abnormal case recovered!")
                    logging_command("Abnormal case recovered!")
                    if parking_type == "in":
                        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": 0}})
                    elif parking_type == "out":
                        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": 0}})
        elif abnormal_value == 1:
            if sensor_count == 2:
                next_value = check_sensor_states_two()
                if prev_value == 0 and next_value == 0:
                    abnormal_state = False
                    #print("Abnormal case recovered!")
                    logging_command("Abnormal case recovered!")
                    if parking_type == "in":
                        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": 0}})
                    elif parking_type == "out":
                        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": 0}})
                elif prev_value == 1 and next_value == 1:
                    abnormal_state = False
                    #print("Abnormal case recovered!")
                    logging_command("Abnormal case recovered!")
                    if parking_type == "in":
                        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": 0}})
                    elif parking_type == "out":
                        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": 0}})
            elif sensor_count == 3:
                next_value = check_sensor_states()
                if next_value == 1:
                    abnormal_state = False
                    #print("Abnormal case recovered!")
                    logging_command("Abnormal case recovered!")
                    if parking_type == "in":
                        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": 0}})
                    elif parking_type == "out":
                        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": 0}})
        elif abnormal_value == 2:
            if sensor_count == 2:
                next_value = check_sensor_states_two()
            elif sensor_count == 3:
                next_value = check_sensor_states()
                if next_value == 100 or next_value == 111 or next_value == 110:
                    abnormal_state = False
                    #print("Abnormal case recovered!")
                    logging_command("Abnormal case recovered!")
                    if parking_type == "in":
                        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": 0}})
                    elif parking_type == "out":
                        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": 0}})
        elif abnormal_value == 3:
            if sensor_count == 2:
                next_value = check_sensor_states_two()
            elif sensor_count == 3:
                next_value = check_sensor_states()
                if next_value == 0:
                    abnormal_state = False
                    #print("Abnormal case recovered!")
                    logging_command("Abnormal case recovered!")
                    if parking_type == "in":
                        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": 0}})
                    elif parking_type == "out":
                        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": 0}})
        elif abnormal_value == 4:
            if sensor_count == 2:
                next_value = check_sensor_states_two()
            elif sensor_count == 3:
                next_value = check_sensor_states()
                if next_value == 1:
                    abnormal_state = False
                    #print("Abnormal case recovered!")
                    logging_command("Abnormal case recovered!")
                    if parking_type == "in":
                        update_one({"name": parking_site_name}, {"$set": {"in_abnormal": 0}})
                    elif parking_type == "out":
                        update_one({"name": parking_site_name}, {"$set": {"out_abnormal": 0}})
        else:
            abnormal_state = True
    get_data(parking_site_name)

#MongoDB holbolt
def check_connection():
    result = db.command("ping")
    if result["ok"] == 1:
        #print("active")
        logging_command("Server Connection: OK!")
    else:
        #print("inactive")
        logging_command("Server Connection: Down!")

def get_data(name):
    query = {"name": "{}".format(name)}
    cursor = collection.find(query)
    for document in cursor:
        #print(document)
        document = document
    return document
        
def update_one(query, new_value):
    result = collection.update_one(query, new_value)
    #print(result.modified_count, "document updated")
    
def query_command(search):
    myquery = search
    mydocs = collection.find({}, myquery)
    for doc in mydocs:
        #print(doc)
        doc = doc
        
def text_trim(start_word, end_word, data):
    #print(data)
    start = start_word
    #print(start)
    end = end_word
    #print(end)
    start_index = data.index(start)+len(start)
    end_index = data.index(end, start_index)
    result = data[start_index:end_index]
    #print(result)
    return result
    
def check_counts():
    check_connection()
    data = get_data(parking_site_name)
    current_count = text_trim("'total_count': ", ",", str(data))
    count = int(current_count)
    print(count)
    logging_command("Current parked car: {}".format(count))    
    in_current = text_trim("in_count': ", ", ", str(data))
    in_count = int(in_current)
    logging_command("All entered car: {}".format(in_count))
    #print(in_count)
    out_current = text_trim("out_count': ", ",", str(data))
    out_count = int(out_current)
    logging_command("All exit car: {}".format(out_count))
    car_back_count_current = text_trim("in_car_back_count': ", ",", str(data))
    car_back_count = int(car_back_count_current)
    logging_command("All backed car: {}".format(car_back_count))
    return out_count, in_count, count, car_back_count

#Server luu mashin butsaj uharsaniig medegdeh
def car_backed():
    global car_back_count, parking_type
    #print("Car back detected!")
    logging.info("Car back detected!")
    car_back_count += 1
    logging.info(car_back_count)
    if parking_type == "in": 
        update_one({"name": parking_site_name}, {"$set": {"in_car_back_count": car_back_count}})
        update_one({"name": parking_site_name}, {"$set": {"in_car_back_time": str(strftime("%m%d%Y, %H:%M:%S"))}})
    elif parking_type == "out":
        update_one({"name": parking_site_name}, {"$set": {"out_car_back_count": car_back_count}})
        update_one({"name": parking_site_name}, {"$set": {"out_car_back_time": str(strftime("%m%d%Y, %H:%M:%S"))}})
    #tcp_send(TCP_IP, TCP_PORT, "Car backing detected!")

def car_backing():
    logging.info("Car backing!")

def duo_car():
    logging.info("Duo car!")

def finish_parking():
    global out_count, parking_type
    out_count, in_count, count, car_back_count = check_counts()
    if parking_type == "in":
        count += 1
        in_count += 1
        update_one({"name": parking_site_name}, {"$set": {"total_count": count}})
        update_one({"name": parking_site_name}, {"$set": {"in_count": in_count}})
        logging_command("Counted car: {count}".format(count=in_count))
    elif parking_type == "out":
        count -+ 1
        out_count += 1
        update_one({"name": parking_site_name}, {"$set": {"total_count": count}})
        update_one({"name": parking_site_name}, {"$set": {"out_count": in_count}})
        logging_command("Counted car: {count}".format(count=out_count))
    logging_command("Car finished!")    
    #tcp_send(TCP_IP, TCP_PORT, "1 car in!")

def error_case(error_text, error_number):
    global parking_type
    logging_command(error_text)
    if parking_type == "in":
        update_one({"name": parking_site_name}, {"$set": {"in_error": error_number}})
        update_one({"name": parking_site_name}, {"$set": {"in_error_last_state_text": error_text}})
        update_one({"name": parking_site_name}, {"$set": {"in_error_last_state_time": str(strftime("%m%d%Y, %H:%M:%S"))}})
    elif parking_type == "out":
        update_one({"name": parking_site_name}, {"$set": {"out_error": error_number}})
        update_one({"name": parking_site_name}, {"$set": {"out_error_last_state_text": error_text}})
        update_one({"name": parking_site_name}, {"$set": {"out_error_last_state_time": str(strftime("%m%d%Y, %H:%M:%S"))}})

#Prev, Next value bolowsruulalt 2 sensortoi
def zero_case_two(next_value):
    command_text = "nothing"
    if next_value == 0:
        command_text = "waiting"
    elif next_value == 1:
        command_text = "car comes"
        #tcp_send(TCP_IP, TCP_PORT, "Car come!")
    elif next_value == 10:
        command_text = "Wrong side coming"
        abnormal_state = True
        abnormal_state_recover(1)
    elif next_value == 11:
        command_text = "Car coming from two side"
        abnormal_state = True
        abnormal_state_recover(4)
    return command_text

def one_case_two(next_value):
    command_text = "nothing"
    if next_value == 0:
        command_text = "Car backing"
        car_backed()
    elif next_value == 1:
        command_text = "car waiting"
    elif next_value == 10:
        command_text = "car finishing"
    elif next_value == 11:
        command_text = "Car moving / next car coming"
        #abnormal_state = True
        #abnormal_state_recover(1)
    return command_text
    
def ten_case_two(next_value):
    dcommand_text = "nothing"
    if next_value == 0:
        command_text = "Finish"
        finish_parking()
    elif next_value == 1:
        command_text = "Car backing"
        car_backed()
    elif next_value == 10:
        command_text = "Car waiting"
    elif next_value == 11:
        command_text = "Car moving / next car coming"
        abnormal_state = True
        abnormal_state_recover(2)
    return command_text
    
def eleven_case_two(next_value):
    command_text = "nothing"
    if next_value == 0:
        command_text = "Error"
        error_case(command_text, 1)
    elif next_value == 1:
        command_text = "Car backing"
        car_backed()
    elif next_value == 10:
        command_text = "Big car moving"
    elif next_value == 11:
        command_text = "Car waiting"
    return command_text


    command_text = "nothing"
    if next_value == 0:
        command_text = "waiting"
    elif next_value == 1:
        command_text = "car comes"
    elif next_value == 10:
        command_text = "Error:102"
    elif next_value == 11:
        command_text = "Error:102"
    elif next_value == 100:
        command_text = "Wrong side car"
        abnormal_state_recover(1)
    elif next_value == 101:
        command_text = "Car at two side"
        abnormal_state_recover(2)
    elif next_value == 110:
        command_text = "Wrong side car"
        abnormal_state_recover(1)
    elif next_value == 111:
        command_text = "Error:106"

def startup():
    global out_count, in_count, count, car_back_count, Contact, TCP_IP, TCP_PORT
    get_info_config()
    out_count, in_count, count, car_back_count = check_counts()
    sensor_init()
    #tcp_send(TCP_IP, TCP_PORT, "Initiation successful!")
    #Sensoroos HIGH, LOW bolj bga eventiig awah heseg
    
startup()

tcp_notification = False
#Undsen function
while True:       
    prev_value = check_sensor_states_two()
    time.sleep(1)
    next_value = check_sensor_states_two()
    if prev_value == 0:
        val = zero_case_two(next_value)
    elif prev_value == 1:
        val = one_case_two(next_value)
    elif prev_value == 10:
        val = ten_case_two(next_value)
    elif prev_value == 11:
        val = eleven_case_two(next_value)
    print(val)