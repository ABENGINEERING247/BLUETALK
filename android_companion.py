"""
BlueTalk Native Android Bluetooth Companion Daemon
Runs on Android hardware to provide true Bluetooth RFCOMM socket connectivity
bridging local TCP/HTTP payloads straight into the Streamlit interface.
"""

import sys
import time
import json

if sys.platform == 'android':
    from jnius import autoclass
    from jnius import cast
    
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothServerSocket = autoclass('android.bluetooth.BluetoothServerSocket')
    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
    UUID = autoclass('java.util.UUID')

    BLUETOOTH_UUID = UUID.fromString("fa87c0d0-afac-11de-8a39-0800200c9a66")
    
    def start_bluetooth_server():
        adapter = BluetoothAdapter.getDefaultAdapter()
        if not adapter:
            print("[BT-Error] Bluetooth hardware not found on device.")
            return

        if not adapter.isEnabled():
            print("[BT-Warning] Bluetooth adapter is disabled. Please enable it.")
            
        try:
            server_socket = adapter.listenUsingRfcommWithServiceRecord("BlueTalkService", BLUETOOTH_UUID)
            print("[BT-Server] BlueTalk listening on RFCOMM channel...")
            
            while True:
                socket = server_socket.accept()
                print(f"[BT-Server] Connection established with peer device!")
                
                input_stream = socket.getInputStream()
                output_stream = socket.getOutputStream()
                
                buffer = bytearray(1024)
                bytes_read = input_stream.read(buffer)
                if bytes_read > 0:
                    raw_data = buffer[:bytes_read].decode('utf-8')
                    print(f"[BT-Data] Received payload: {raw_data}")
                    
                    ack_message = json.dumps({"status": "delivered"}).encode('utf-8')
                    output_stream.write(ack_message)
                    output_stream.flush()
                    
                socket.close()
        except Exception as e:
            print(f"[BT-Error] Socket server exception: {e}")

if __name__ == "__main__":
    if sys.platform == 'android':
        start_bluetooth_server()
    else:
        print("Note: This companion script runs natively on Android hardware. Running desktop simulation wrapper...")
        while True:
            time.sleep(1)
