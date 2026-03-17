from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pycaw.pycaw as pycaw
from comtypes import CLSCTX_ALL

try:
    devices = AudioUtilities.GetSpeakers()
    print(f"Devices type: {type(devices)}")
    print(f"Devices dir: {dir(devices)}")
    
    # Try to find Activate or similar
    if hasattr(devices, 'Activate'):
        print("Devices has Activate")
    else:
        print("Devices DOES NOT have Activate")

    # Inspect pycaw module
    print(f"Pycaw dir: {dir(pycaw)}")
    
except Exception as e:
    print(f"Error: {e}")
