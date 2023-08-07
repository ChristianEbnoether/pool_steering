
import asyncio

from bleak import BleakClient

import time

from decodeInt import Messure

address = "C0:00:00:00:76:55"

# MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"

MODEL_NBR_UUID = "0000180D-0000-1000-8000-00805F9B34FB"

Battery_Service = "00002a19-0000-1000-8000-00805f9b34fb"

Vendor_specific = "0000ff10-0000-1000-8000-00805f9b34fb"

"""

00001800-0000-1000-8000-00805f9b34fb (Handle: 1): Generic Access Profile

00001801-0000-1000-8000-00805f9b34fb (Handle: 8): Generic Attribute Profile

0000180a-0000-1000-8000-00805f9b34fb (Handle: 12): Device Information

0000180f-0000-1000-8000-00805f9b34fb (Handle: 31): Battery Service

0000ff01-0000-1000-8000-00805f9b34fb (Handle: 36): Vendor specific

"""

class Messure(object):

    def __init__(self, frame : str) -> None:

        self.frame = frame

       

        self.packet = self.decode(frame)

       

        self.data = self.packet[0]

        self.constant = self.packet[1]

        self.product_name_code = self.packet[2]

       

        self.hold_reading = self.packet[17] >> 4

        self.backlight_status = (self.packet[17] & 0x0F) >> 3

        self.battery = self.decode_position(15)

       

        self.ec = self.decode_position(5)

        self.tds = self.decode_position(7)

        self.salt_tds = self.decode_position(9)

        self.salt_sg = self.decode_position(11) ##TO DO

        self.ph = self.decode_position(3)/100

        self.orp = self.decode_position(20)

        self.temperature = self.decode_position(13)/10

       

    def decode(self, byte_frame : bytes ):

        frame_array = [int(x) for x in byte_frame]

        size = len(frame_array)

        for i in range(size-1, 0 , -1):

            tmp=frame_array[i]

            hibit1=(tmp&0x55)<<1

            lobit1=(tmp&0xAA)>>1

            tmp=frame_array[i-1]

            hibit=(tmp&0x55)<<1

            lobit=(tmp&0xAA)>>1

            frame_array[i]=0xff -(hibit1|lobit)

            frame_array[i-1]= 0xff -(hibit|lobit1)

       

        return frame_array

   

    def reverse_bytes(self, bytes : list):

        return (bytes[0] << 8) + bytes[1]

       

    def decode_position(self,idx):

        return self.reverse_bytes(self.packet[idx:idx+2])

   

    def show_values(self):

        return_string = f"h=[{self.hold_reading}/bl={self.backlight_status}/B={self.battery}] EC={self.ec:4}  TDS={self.tds:4}  SALT(TDS)={self.salt_tds:4}  SALT(S.G.)={self.salt_sg:4}  pH={self.ph:4}  ORP(mV)={self.orp:4}  Temperature(C)={self.temperature:4} "

        return return_string

   

async def main(address):

    async with BleakClient(address) as client:

        print(f"Connected: {client.is_connected}")

       

        paired = await client.pair(protection_level=2)

        print(f"Paired: {paired}")

       

        old_time = time.time()

        print(time.time() - old_time)

        while True:

            model_number = await client.read_gatt_char(Vendor_specific)    

            print(Messure(model_number).show_values())

            time.sleep(1)

asyncio.run(main(address))
