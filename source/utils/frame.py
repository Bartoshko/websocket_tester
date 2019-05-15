from time import time

def frame_builder(id_0, id_1, distance, signal=-60.02, fpp=-76.01, time_data=0):
        if time_data != 0:
            actual_time = time_data
        else:
            actual_time = time()
        return {
            'did2': id_0,
            'did1': id_1,
            'dist': distance,
            'signal': signal,
            'fpp': fpp,
            'time': actual_time
        }
