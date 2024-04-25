import serial
import struct
import math
from time import sleep
from numpy import arange

def convert_freq_to_hex_data(frequency):
    wanted_freq_bytes = struct.pack('i', frequency)
    freq_command ='AA 43'
    #tmp = []
    for bit in wanted_freq_bytes[::-1]:
        k = str(hex(bit))[2:]
        if len(k) == 1:
            freq_command = freq_command + ' 0'
        else:
            freq_command = freq_command + ' '
        freq_command = freq_command + k
        #tmp.append(bit)
    #print(freq_command)
    return freq_command


def convert_voltage_to_hex_data(voltage):
    wanted_voltage_bytes = struct.pack('h', int(voltage*100))
    #print(wanted_voltage_bytes)
    voltage_command ='AA 46'
    #tmp = []
    for bit in wanted_voltage_bytes[::-1]:
        k = str(hex(bit))[2:]
        if len(k) == 1:
            voltage_command = voltage_command + ' 0'
        else:
            voltage_command = voltage_command + ' '
        voltage_command = voltage_command + k
        #tmp.append(bit)
    #print(freq_command)
    return voltage_command

def set_freq(frequency):
    ser.write(bytearray.fromhex(convert_freq_to_hex_data(frequency)))
    b = ser.readline()
    c = ser.readline()
    #print(b)
    #print(c)

def set_U(voltage): # inner up to 40V
    ser.write(bytearray.fromhex(convert_voltage_to_hex_data(voltage)))
    b = ser.readline()
    c = ser.readline()
    #print(b)
    #print(c)


def read_all_values():
    ser.write(bytearray.fromhex('AA 48'))
    a = ser.read(200)
    #print(a)

    # print(struct.unpack('i', a[11:7:-1])[0]) # frequency
    # print(struct.unpack('f', a[15:11:-1])[0]) # Z
    # print(struct.unpack('f', a[:15:-1])[0]*57.2957795) # phase

    freq = struct.unpack('i', a[11:7:-1])[0]

    Z = struct.unpack('f', a[15:11:-1])[0]
    #Y = 1/Z
    phase = struct.unpack('f', a[:15:-1])[0]*57.2957795
    phi_z = struct.unpack('f', a[:15:-1])[0]
    phi_y = -phi_z
    Rs = Z * math.cos(phi_z)
    Xs = Z * math.sin(phi_z)
    #Gp = Y * math.cos(phi_y)
    #Bp = math.sin(phi_y)
    #Rp = 1 /Gp
    #Xp = 1 /Bp
    #Gs = 1 /Rs
    #Bs = 1 /Xs
    C = -1/(2*math.pi*freq*Xs)
    L = -2*math.pi*freq*Xs
    # print(Rs)
    # print(C)
    # print(L)
    return [freq, Rs, C, L, Z, phase]


def create_sweep_array(coarse_flag=False):
    steps_fine = [1, 10, 100, 1000, 10000, 100000]
    steps_coarse = [5, 300, 3000, 3000, 30000, 200000]

    if coarse_flag == True:
        step = steps_coarse
    else:
        step = steps_fine

    total_list = list(range(25, 100, step[0])) + list(range(100, 1000, step[1])) + list(range(1000, 10000, step[2])) \
                 + list(range(10000, 100000, step[3]))  + list(range(100000, 1000000, step[4]))  + list(range(1000000, 3000001, step[5]))

    return total_list


def RLC_frequency_sweep(coarce_flag=False):

    freq_array_for_sweep = create_sweep_array(coarce_flag)

    #freq_array_for_sweep = [25, 1000, 10000, 100000]
    result_data_Z = []
    result_data_phase = []
    result_data_R = []
    result_data_C = []
    result_data_L = []
    for i in freq_array_for_sweep:
        set_freq(i)
        sleep(1)
        temp_params = read_all_values()
        result_data_R.append(temp_params[1])
        result_data_C.append(temp_params[2])
        result_data_L.append(temp_params[3])
        result_data_Z.append(temp_params[4])
        result_data_phase.append(temp_params[5])

    #[freq, Rs, C, L, Z, phase] returned from read_all_values() func

    return [freq_array_for_sweep, result_data_R, result_data_C, result_data_L, result_data_Z, result_data_phase]



def CV_sweep(step=0.1, start=0, stop=0):  #step min = 0.01
    set_freq(1000000)
    result_data_Z = []
    result_data_phase = []
    result_data_R = []
    result_data_C = []
    result_data_L = []
    voltage_sweep = list(arange(start, stop, step))
    for i in voltage_sweep:
        set_U(i)
        sleep(1)
        temp_params = read_all_values()
        result_data_R.append(temp_params[1])
        result_data_C.append(temp_params[2])
        result_data_L.append(temp_params[3])
        result_data_Z.append(temp_params[4])
        result_data_phase.append(temp_params[5])

    set_U(0)
    return [voltage_sweep, result_data_R, result_data_C, result_data_L, result_data_Z, result_data_phase]


#######################################################################################################################

ser = serial.Serial('COM3', 9600, timeout=0.5, bytesize=8, parity=serial.PARITY_NONE, stopbits=1)



import matplotlib.pyplot as plt
#result = RLC_frequency_sweep(True)
#result = CV_sweep(0.05, 0, 20)
# fig, ax = plt.subplots()
# x = result[0]
# y = result[2]
# ax.plot(x, y, linewidth=2.0)
# plt.show()



# wanted_freq = 1000
# set_freq(wanted_freq)
# print(read_all_values())


ser.close()

