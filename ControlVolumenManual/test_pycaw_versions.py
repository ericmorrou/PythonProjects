from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import comtypes
from ctypes import cast, POINTER

def test_method_1():
    print("Testing Method 1 (Standard)...")
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        print("Method 1 SUCCESS")
        return volume
    except Exception as e:
        print(f"Method 1 FAILED: {e}")
        return None

def test_method_2():
    print("\nTesting Method 2 (MMDeviceEnumerator)...")
    try:
        from pycaw.utils import AudioUtilities
        # In some versions, this is the way
        volume = AudioUtilities.GetAudioEndpointVolume()
        print("Method 2 SUCCESS")
        return volume
    except Exception as e:
        print(f"Method 2 FAILED: {e}")
        return None

def test_method_3():
    print("\nTesting Method 3 (Direct COM)...")
    try:
        from pycaw.pycaw import IMMDeviceEnumerator, CLSID_MMDeviceEnumerator
        enumerator = comtypes.CoCreateInstance(
            CLSID_MMDeviceEnumerator,
            IMMDeviceEnumerator,
            comtypes.CLSCTX_ALL
        )
        endpoint = enumerator.GetDefaultAudioEndpoint(0, 1)
        interface = endpoint.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        print("Method 3 SUCCESS")
        return volume
    except Exception as e:
        print(f"Method 3 FAILED: {e}")
        return None

v1 = test_method_1()
v2 = test_method_2()
v3 = test_method_3()
