import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VolumeController:
    def __init__(self):
        # En esta versión de pycaw, GetSpeakers() devuelve un envoltorio con la propiedad EndpointVolume
        try:
            devices = AudioUtilities.GetSpeakers()
            self.volume = devices.EndpointVolume
        except Exception as e:
            # Plan B: Intentar el método manual si el envoltorio falla
            print(f"Error inicializando pycaw: {e}. Intentando fallback...")
            from pycaw.pycaw import IAudioEndpointVolume
            import comtypes
            interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))

        self.vol_range = self.volume.GetVolumeRange()
        self.min_vol = self.vol_range[0]
        self.max_vol = self.vol_range[1]
        self.vol = 0
        self.vol_bar = 400
        self.vol_per = 0

    def get_current_volume(self):
        return self.volume.GetMasterVolumeLevel()

    def set_volume(self, length, min_dist=50, max_dist=300):
        # Interpolate length to volume range
        self.vol = np.interp(length, [min_dist, max_dist], [self.min_vol, self.max_vol])
        self.vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
        self.vol_per = np.interp(length, [min_dist, max_dist], [0, 100])
        
        self.volume.SetMasterVolumeLevel(self.vol, None)
        return self.vol_per, self.vol_bar

    def get_stats(self):
        return self.vol_per, self.vol_bar
