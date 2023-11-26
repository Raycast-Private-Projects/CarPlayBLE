import ubluetooth as bluetooth
from micropython import const
from ble_advertising import advertising_payload
import time
import machine


Directions = [
    "ARRIVE", "ARRIVE_LEFT", "ARRIVE_RIGHT", "CONTINUE_LEFT", "CONTINUE_RETURN",
    "CONTINUE_RIGHT", "CONTINUE_SLIGHT_LEFT", "CONTINUE_SLIGHT_RIGHT", "CONTINUE_STRAIGHT",
    "DEPART", "FORK", "POINTER", "ROTATORY_EXIT", "ROTATORY_EXIT_INVERTED", "ROTATORY_LEFT",
    "ROTATORY_LEFT_INVERTED", "ROTATORY_RIGHT", "ROTATORY_RIGHT_INVERTED", "ROTATORY_SHARP_LEFT",
    "ROTATORY_SHARP_LEFT_INVERTED", "ROTATORY_SHARP_RIGHT", "ROTATORY_SHARP_RIGHT_INVERTED",
    "ROTATORY_SLIGHT_LEFT", "ROTATORY_SLIGHT_LEFT_INVERTED", "ROTATORY_SLIGHT_RIGHT",
    "ROTATORY_SLIGHT_RIGHT_INVERTED", "ROTATORY_STRAIGHT", "ROTATORY_STRAIGHT_INVERTED",
    "ROTATORY_TOTAL", "ROTATORY_TOTAL_INVERTED", "SHARP_LEFT", "SHARP_RIGHT", "SLIGHT_LEFT",
    "SLIGHT_RIGHT", "UNKNOWN"
]

_IO_CAPABILITY_NO_INPUT_OUTPUT = const(3)

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)
_IRQ_GATTS_INDICATE_DONE = const(20)


SERVICE_UUID_STR = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
SERVICE_UUID = bluetooth.UUID(SERVICE_UUID_STR)

DESTINATION_UUID_STR = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
DESTINATION_UUID = bluetooth.UUID(DESTINATION_UUID_STR)
DESTINATION_CHAR = (bluetooth.UUID(DESTINATION_UUID_STR), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,)

ETA_UUID_STR = "ca83fac2-2438-4d14-a8ae-a01831c0cf0d"
ETA_UUID = bluetooth.UUID(ETA_UUID_STR)
ETA_CHAR = (bluetooth.UUID(ETA_UUID_STR), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,)

DIRECTION_UUID_STR = "dfc521a5-ce89-43bd-82a0-28a37f3a2b5a"
DIRECTION_UUID = bluetooth.UUID(DIRECTION_UUID_STR)
DIRECTION_CHAR = (bluetooth.UUID(DIRECTION_UUID_STR), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,)

DIRECTION_DISTANCE_UUID_STR = "0343ff39-994e-481b-9136-036dabc02a0b"
DIRECTION_DISTANCE_UUID = bluetooth.UUID(DIRECTION_DISTANCE_UUID_STR)
DIRECTION_DISTANCE_CHAR = (bluetooth.UUID(DIRECTION_DISTANCE_UUID_STR), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,)

ETA_MINUTES_UUID_STR = "563c187d-ff17-4a6a-8061-ca9b7b70b2b0"
ETA_MINUTES_UUID = bluetooth.UUID(ETA_MINUTES_UUID_STR)
ETA_MINUTES_CHAR = (bluetooth.UUID(ETA_MINUTES_UUID_STR), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,)

DISTANCE_UUID_STR = "8bf31540-eb0d-476c-b233-f514678d2afb"
DISTANCE_UUID = bluetooth.UUID(DISTANCE_UUID_STR)
DISTANCE_CHAR = (bluetooth.UUID(DISTANCE_UUID_STR), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,)

DIRECTION_PRECISE_UUID_STR = "a602346d-c2bb-4782-8ea7-196a11f85113"
DIRECTION_PRECISE_UUID = bluetooth.UUID(DIRECTION_PRECISE_UUID_STR)
DIRECTION_PRECISE_CHAR = (bluetooth.UUID(DIRECTION_PRECISE_UUID_STR), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,)

MapsConnectService = (SERVICE_UUID, (
DESTINATION_CHAR, ETA_CHAR, DIRECTION_CHAR, DIRECTION_DISTANCE_CHAR, ETA_MINUTES_CHAR, DISTANCE_CHAR,
DIRECTION_PRECISE_CHAR),)

SERVICES = (MapsConnectService,)

value_handle = 0
dict = {}
dict['Maps data'] = {}
dict['Maps data']["Time"] = {}
dict['Maps data']["Travel Time"] = {}
dict['Maps data']["Arival Time"] = {}
dict['Maps data']["Direction"] = {}
class BLEMapsService:
    #def __init__(self, ble, name="mpy-BT"):
    #buzzer = machine.Pin(14, machine.Pin.OUT)
    DataDict = {}
    #value_handle = 0
    ReadData = False
    def __init__(self, name="mpy-BT"):
        #self._ble = ble
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.config(mtu=400)
        self._ble.config(io=_IO_CAPABILITY_NO_INPUT_OUTPUT)
        print(self._ble.config('mac')[1].hex(":"))
        self._ble.irq(self._irq)
        #((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        ((self.MapsConnect)) = self._ble.gatts_register_services(SERVICES)
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[SERVICE_UUID])
        self._advertise()

    def _irq(self, event, data):
        global value_handle
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
            #buzzer.high()
            #time.sleep(2)
            #buzzer.low()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            print("Received Data")
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            decoded_value = value.decode('utf-8').replace(u'\xa0', ' ')
            self.ReadData = True
            #if value_handle == self._handle_rx and self._write_callback:
            #    self._write_callback(value)
            if value_handle == 21:
                print('Time: ', decoded_value)
                self.DataDict["Time"] = decoded_value
            elif value_handle == 29:
                print('Travel Time: ', decoded_value)
                self.DataDict["TravelTime"] = decoded_value
            elif value_handle == 23:
                print('Arival Time', decoded_value)
                self.DataDict["ArivalTime"] = decoded_value
            elif value_handle == 27:
                print('Street: ', decoded_value)
                self.DataDict["Street"] = decoded_value
            elif value_handle == 31:
                print('Distance: ', decoded_value)
                self.DataDict["Distance"] = decoded_value
            elif value_handle == 25:
                print('Distance Till: ', decoded_value)
                self.DataDict["DistanceTill"] = decoded_value
            elif value_handle == 33:
                print('Direction: ', decoded_value)
                self.DataDict["Direction"] = decoded_value
            #print("\n\n")
#            print("Conn Handle: ", conn_handle  )
#            print("Value Handle: ", value_handle)
#            print("Value: ", value.decode('utf-8'))
        #elif event == _IRQ_MTU_EXCHANGED:
        #    conn_handle, mtu = data
        #    self._ble.config(mtu=mtu)
        else:
            print("Received Unknown Data")
            print("Data:")
            print("Event: ", event)
            print("Data: ", data)
            #buzzer.high()
            #time.sleep(1)
            #buzzer.low()
    #def send(self, data):
    #    for conn_handle in self._connections:
    #        self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback
    def GetData(self):
        return self.DataDict
    def ResetRead(self):
        self.ReadData = False
        return
    def NewBLEData(self):
        return self.ReadData
def BluetoothService():
    #ble = bluetooth.BLE()
    #Maps = BLEMapsService(ble)
    Maps = BLEMapsService()
    def on_rx(v):
        print("RX", v)

    Maps.on_write(on_rx)
#BluetoothService()
def empty():
    pass
Maps = BLEMapsService()
DataReadTimer = 0
ReadDelay = 3 # 3 seconds delay before setting vars
while True:
    CurrentTick = time.ticks_ms()
    #empty()
    #time.sleep(3)

    if Maps.NewBLEData() and CurrentTick >= DataReadTimer: # Parse Data
        DataReadTimer = CurrentTick + ReadDelay * 1000
        Maps.ResetRead()
        Data = Maps.GetData()
        if "Time" in Data.keys():
            Time = Data["Time"]
            #print('Time: ', Time)
            split = Time.split(":")
            if "AM" in Time:
                dict['Maps data']["Time"]["AmPm"] = "AM"
            elif "PM" in Time:
                dict['Maps data']["Time"]["AmPm"] = "PM"
            else:
                dict['Maps data']["Time"]["AmPm"] = ""
            dict['Maps data']["Time"]["Minute"] = int(split[1].split(" ")[0])
            dict['Maps data']["Time"]["Hour"] = int(split[0])
            #print(dict['Maps data']["Time"])
        if "TravelTime" in Data.keys():
            TravelTime = Data["TravelTime"]
            #print('Travel Time: ', TravelTime)
            split = TravelTime.split(" ")
            if len(split) == 4:
                dict['Maps data']["Travel Time"]["Minute"] = int(split[3])
                dict['Maps data']["Travel Time"]["Hour"] = int(split[0])
            elif len(split) == 2:
                dict['Maps data']["Travel Time"]["Minute"] = int(split[0])
                dict['Maps data']["Travel Time"]["Hour"] = int(0)
            else:
                dict['Maps data']["Travel Time"]["Minute"] = int(0)
                dict['Maps data']["Travel Time"]["Hour"] = int(0)
                print("Error!")
            #print(dict['Maps data']["Travel Time"])
        if "ArivalTime" in Data.keys():
            ArivalTime = Data["ArivalTime"]
            #print('Arival Time', ArivalTime)
            split = ArivalTime.split(":")
            if "AM" in ArivalTime:
                dict['Maps data']["Arival Time"]["AmPm"] = "AM"
            elif "PM" in ArivalTime:
                dict['Maps data']["Arival Time"]["AmPm"] = "PM"
            else:
                dict['Maps data']["Arival Time"]["AmPm"] = ""
                dict['Maps data']["Arival Time"]["Minute"] = int(split[1].split(" ")[0])
                dict['Maps data']["Arival Time"]["Hour"] = int(split[0])
            #print(dict['Maps data']["Arival Time"])
        if "Street" in Data.keys():
            dict["Maps data"]["Street"] = Data["Street"]
        if "Distance" in Data.keys():
            dict["Maps data"]["Distance"] = Data["Distance"]
        if "DistanceTill" in Data.keys():
            dict["Maps data"]["Distance Till"] = Data["DistanceTill"]
        if "Direction" in Data.keys():
            dict["Maps data"]["Direction"]["ID"] = Data["Direction"]
            dict["Maps data"]["Direction"]["Direction"] = Directions[int(Data["Direction"])]
        print("Maps Data: ", dict)
# if "secret" in raw_file_content:
