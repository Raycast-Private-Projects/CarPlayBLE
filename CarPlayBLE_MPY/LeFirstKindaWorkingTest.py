import ubluetooth as bluetooth
from micropython import const
from ble_advertising import advertising_payload
import time
import machine
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
#((MapsConnect)) = ble.gatts_register_services(SERVICES)

def on_write(char):
    uuid = str(char.uuid())
    value = char.value().decode('utf-8')

    if uuid == DESTINATION_UUID:
        print("Destination:", value)
    elif uuid == ETA_UUID:
        print("ETA:", value)
    elif uuid == DIRECTION_UUID:
        print("Direction:", value)
    else:
        print("UUID: ", uuid)
        print("Value: ", value)
    # Add other cases for the remaining characteristics

#def _irq(self, event, data):
    # Track connections so we can send notifications.
#    if event == _IRQ_CENTRAL_CONNECT:
        #conn_handle, _, _ = data
        #print("New connection", conn_handle)
        #self._connections.add(conn_handle)
#        print("Connected")
#    elif event == _IRQ_CENTRAL_DISCONNECT:
        #conn_handle, _, _ = data
        #print("Disconnected", conn_handle)
        #self._connections.remove(conn_handle)
        # Start advertising again to allow a new connection.
        #self._advertise()
#        print("disconnected")
#    elif event == _IRQ_GATTS_WRITE:
#        print("Value received?")
        #conn_handle, value_handle = data
        #value = self._ble.gatts_read(value_handle)
        #if value_handle == self._handle_rx and self._write_callback:
           #self._write_callback(value)
        
# Set callback for characteristic write events
#DESTINATION_CHAR.callback(on_write)
#ETA_CHAR.callback(on_write)
#DIRECTION_CHAR.callback(on_write)
#DIRECTION_DISTANCE_CHAR.callback(on_write)
#ETA_MINUTES_CHAR.callback(on_write)
#DISTANCE_CHAR.callback(on_write)
#DIRECTION_PRECISE_CHAR.callback(on_write)

# Start advertising

#ble.gap_advertise(100, bytearray(SERVICE_UUID))
#print("Advertising...")

#def prettify(mac_string):
#    return ':'.join('%02x' % ord(b) for b in mac_string)

class BLEMapsService:
    #def __init__(self, ble, name="mpy-BT"):
    #buzzer = machine.Pin(14, machine.Pin.OUT)
    def __init__(self, name="mpy-BT"):
        #self._ble = ble
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.config(mtu=400)
        print(self._ble.config('mac')[1].hex(":"))
        self._ble.irq(self._irq)
        #((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        ((self.MapsConnect)) = self._ble.gatts_register_services(SERVICES)
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[SERVICE_UUID])
        self._advertise()

    def _irq(self, event, data):
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
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            #if value_handle == self._handle_rx and self._write_callback:
            #    self._write_callback(value)
            print("Value Handle: ", value_handle)
            print("Value: ", value.decode('utf-8'))
        #elif event == _IRQ_MTU_EXCHANGED:
        #    conn_handle, mtu = data
        #    self._ble.config(mtu=mtu)
        else:
            print("Unknown event")
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

def Test():
    #ble = bluetooth.BLE()
    #Maps = BLEMapsService(ble)
    Maps = BLEMapsService()
    def on_rx(v):
        print("RX", v)

    Maps.on_write(on_rx)
Test()
def empty():
    pass
while True:
    empty()
    time.sleep(1)
