import socket
import json

class SolsTiS:
    """
    When operating the M-Squared Laser System through this class method, call functions via SolsTiSObject.function(params).
    Please see the TCP/IP Protocols document for a full list of functions or find below.
    As a general rule, "report" commands have not been implemented but could be included by querying the ICE Bloc regularly
    for further readout. Since this is very case-specific, it was not necessary in my own implementation.
    """

    def __init__(self,port=39902,host='192.168.1.222'):
        self.laser = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # This initializes the socket with Address Family "INET" and type "SOCK_STREAM".
        self.laser.connect((host,port)) # Connect to the socket with the given host and port information.
        # print(self.start_link()) # Starts the link
        
    def _message(self,task):
        message = {"message":task}
        jsonMessage = json.dumps(message)
        return jsonMessage

    def read_message(self,message):
        """
        Command to decode the reply messages. Assumes that messages received use the following format:
        {"message":{"transmission_id":[id], "op":operation, "parameters":{param_name:param}}}
        """
        load = json.loads(message)
        return load['message']['parameters']

    def send_message(self,task):
        """
        Command to send the message through TCP protocols. Individual commands (see functions below) are
        structured to be in the appropriate dict format already. The private _message function called in this function
        transforms the task to JSON format, which is then sent to the ICE Bloc.
        Returned data will contain the system reply. Each function has it's own dictionary of replies, which are decoded
        in the command function.
        """
        message = self._message(task)
        self.laser.sendall(message.encode())
        data = self.read_message(self.laser.recv(2048))
        return data
    
    def start_link(self,ip_address='192.168.1.108'): # This IP address is the client IP address for the user's computer.
        task = {"transmission_id":[900],
                "op":"start_link",
                "parameters":
                {"ip_address":ip_address}
                }
        recv = self.send_message(task)
        return recv
    
    def ping(self,text):
        """
        This command causes the receiving box to invert the case of the received text and 
        send it back.
        """
        task = {"transmission_id":[901],
                "op":"ping",
                "parameters":
                {"text_in":text}
                }
        recv = self.send_message(task)
        return recv
    
    def set_wave_m(self,wavelength): ## Tune the Wavelength (Wavelength Meter)
        """ Command to tune the wavelength on Solstis 2/3.
        Command: 
            -Wavelength: Tuning Value in nm within the tuning range of the SolsTiS
            -report // optional
        Reply: 
            -status = {0:'command successful',1:'no link to wavelength meter or no meter configured', 2:'wavelength out of range'}
            -report = {0:'task completed', 1:'task failed'}
            -wavelength = float # Most recently obtained wavelength reading from the wavelength meter
            -extended_zone = {0:'current wavelength is not in an extended zone',1:'current wavelength is in an extended zone'}
            -duration = float # Time taken in seconds from receiving the task to transmitting the final report. //Only with the report. 
        """
            
        task = {"transmission_id":[1],
                "op":"set_wave_m",
                "parameters":{
                    "wavelength":[wavelength]
                    }
                }
        recv = self.send_message(task)
        return recv

    def poll_wave_m(self): ## Get Wavelength Tuning Status (Wavelength Meter)
        """ Command to monitor the wavelength tuning process which is currently active. 
        Command: 
            -None
        Reply:
            -status = {0:'tuning software not active', 1: 'no link to wavelength meter or no meter configured', 2:'tuning in progress', 3: 'wavelength is being maintained'}
            -current_wavelength = float # The most recently obtained wavelength reading from the wavelength meter
            -lock_status = {0:'wavelength is not being maintained', 1:'wavelength is being maintained'}
            -extended_zone = {0:'current wavelength is not in an extended zone', 1:'current wavelength is in an extended zone'}
        """
    
        task = {"transmission_id":[2],
                    "op":"poll_wave_m"
                }
        recv = self.send_message(task)
        return recv

    def lock_wave_m(self,operation): ## Lock Wavelength (Wavelength Meter)
        """ Apply or remove the wavelength lock operation.
        Command:
            -operation: "On" or "Off"
        Reply:
            -status = {0:'operation successful',1:'no link to wavelength meter or no meter configured'}
        """
    
        task = {"transmission_id":[3],
                    "op":"lock_wave_m",
                    "parameters":
                    {"operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv

    def stop_wave_m(self): ## Stop Wavelength Tuning (Wavelength Meter)
        """Stop the currently active wavelength tuning operation.
        Command:
            -None
        Reply:
            -status = {0:'operation successful',1:'no link to wavelength meter or no meter configured'}
            -current_wavelength = float #Most recently obtained wavelength reading from wavelength meter.
        """
    
        task = {"transmission_id":[4],
                    "op":"stop_wave_m"
                }
        recv = self.send_message(task)
        return recv

    def move_wave_t(self,wavelength): ## Start Table Tuning (Wavelength Table Tuning)
        """Tune the wavelength with a wavelength table, no wavelength meter. 
        *Note:* This command will FAIL if the wavelength meter is fitted and operating with the SolsTiS. In other words, we shouldn't ever need this.
        
        Command:
            -wavelength
            -report
        Reply:
            -status = {0:'operation successful',1:'no link to wavelength meter or no meter configured'}
        """
        
        task = {"transmission_id":[5],
                    "op":"move_wave_t",
                    "parameters":
                    {"wavelength":[wavelength]
                    }
                }
        recv = self.send_message(task)
        return recv

    def poll_move_wave_t(self): ## Poll Table Tuning (Wavelength Table Tuning)
        """Monitor wavelength tuning.
        Command:
            -None
        Reply:
            -status = {0:'operation successful',1:'no link to wavelength meter or no meter configured'}
            -wavelength = float #The current wavelength the SolsTiS is tuned to. This value will be seen to change if the command is re-issued as the tuning operation takes place.
        """
        
        task = {"transmission_id":[6],
                    "op":"poll_move_wave_t"
                }
        recv = self.send_message(task)
        return recv

    def stop_move_wave_t(self): ## Stop Table Tuning (Wavelength Table Tuning)
        """ Stop wavelength tuning.
        Command:
            -None
        Reply:
            -status = {0:'operation successful',1:'no link to wavelength meter or no meter configured'}
        """
        
        task = {"transmission_id":[7],
                    "op":"stop_move_wave_t"
                }
        recv = self.send_message(task)
        return recv
        
    def tune_etalon(self,setting): ## Tune Etalon
        """ Adjust etalon tuning.
        Command:
            -setting #Etalon Tuning. A percentage where 100 is the maximum
            -report 
        Reply:
            -status = {0:'operation completed',1:'setting out of range',2:'command failed'}
            -report = {0:'task completed',1:'task failed'}
        """
        
        task = {"transmission_id":[8],
                    "op":"tune_etalon",
                    "parameters":
                    {"setting":[setting]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def tune_cavity(self,setting): ## Tune Reference Cavity
        """ Adjust reference cavity.
        Command:
            -setting #Reference cavity tuning
            -report
        Reply:
            -status = {0:'operation completed',1:'setting out of range',2:'command failed'}
            -report = {0:'task completed',1:'task failed'}
        """
        
        task = {"transmission_id":[9],
                    "op":"tune_cavity",
                    "parameters":
                    {"setting":[setting]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def fine_tune_cavity(self,setting): ## Fine Tune Reference Cavity
        """ Adjust reference cavity fine tuning.
        Command:
            -setting #Fine cavity reference tuning
            -report
        Reply:
            -status = {0:'operation completed',1:'setting out of range',2:'command failed'}
            -report = {0:'task completed',1:'task failed'}"""
        
        task = {"transmission_id":[10],
                    "op":"fine_tune_cavity",
                    "parameters":
                    {"setting":[setting]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def tune_resonator(self,setting): ## Tune Resonator
        """ Adjust resonator.
        Command:
            -setting #Resonator tuning
            -report
        Reply:
            -status = {0:'operation completed',1:'setting out of range',2:'command failed'}
            -report = {0:'task completed',1:'task failed'}"""
        
        task = {"transmission_id":[11],
                    "op":"tune_resonator",
                    "parameters":
                    {"setting":[setting]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def fine_tune_resonator(self,setting): ## Fine Tune Resonator
        """ Adjust resonator fine tuning.
        Command:
            -setting #Fine resonator tuning
            -report
        Reply:
            -status = {0:'operation completed',1:'setting out of range',2:'command failed'}
            -report = {0:'task completed',1:'task failed'}"""
        
        task = {"transmission_id":[12],
                    "op":"fine_tune_resonator",
                    "parameters":
                    {"setting":setting
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def etalon_lock(self,operation): ## Etalon Lock
        """ Set or remove etalon lock.
        Command:
            -operation = "on", "off"
            -report
        Reply:
            -status = {0:'operation completed',1:'operation failed'}
            -report = {0:'task completed',1:'task failed'}"""
    
        task = {"transmission_id":[13],
                    "op":"etalon_lock",
                    "parameters":
                    {"operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def etalon_lock_status(self): ## Etalon Lock Status
        """ Obtain etalon lock status.
        Command:
            -None
        Reply:
            -status = {0:'operation completed',1:'operation failed'}
            -condition = {"off": "the lock is off", "on": "the lock is on", "debug": "the lock is in a debug condition",
                "error": "the lock is in error", "search": "the lock search algorithm is active", "low": "the lock is off due to low output"}
        """
        
        task = {"transmission_id":[14],
                    "op":"etalon_lock_status"
                }
        recv = self.send_message(task)
        return recv
        
    def cavity_lock(self,operation): ## Reference Cavity Lock
        """ Set or remove the reference cavity lock.
        Command:
            -operation = "on", "off"
            -report
        Reply:
            -status = {0:'operation completed',1:'operation failed'}
            -report = {0:'task completed',1:'task failed'}
        """
        task = {"transmission_id":[15],
                    "op":"cavity_lock",
                    "parameters":
                    {"operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def cavity_lock_status(self): ## Reference Cavity Lock Status
        """ Obtain reference cavity lock status.
        Command:
            -None
        Reply:
            -status = {0:'operation completed',1:'operation failed'}
            -condition = {"off": "the lock is off", "on": "the lock is on", "debug": "the lock is in a debug condition",
                "error": "the lock is in error", "search": "the lock search algorithm is active", "low": "the lock is off due to low output"}
        """
        
        task = {"transmission_id":[16],
                    "op":"cavity_lock_status"
                }
        recv = self.send_message(task)
        return recv
        
    def ecd_lock(self,operation): ## ECD Lock
        """ Set or remove ECD lock (doubler).
        Command:
            -operation = 
            -report
        Reply:
            -status = {0: "operation completed", 1: "operation failed", 2: "ECD not fitted"}
            -report = {0:'task completed', 1:'task failed'}
        """
        
        task = {"transmission_id":[17],
                    "op":"ecd_lock",
                    "parameters":
                    {"operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def ecd_lock_status(self): ## ECD Lock Status
        """ Obtain ECD lock status.
        Command:
            -None
        Reply:
            -status = {0: 'operation completed', 1: 'command failed'}
            -condition = {"off": "the lock is off", "on": "the lock is on", "debug": "the lock is in a debug condition",
                "error": "the lock is in error", "search": "the lock search algorithm is active", "low": "the lock is off due to low output"}
            -voltage = float #Current ECD Lock voltage
        """
        
        task = {"transmission_id":[18],
                    "op":"ecd_lock_status"
                }
        recv = self.send_message(task)
        return recv
    
    def monitor_a(self,signal): ## Apply monitor A
        """ This command switches the requested signal to monitor A output port.
        Command:
            -signal = {"etalon dither": 1, "etalon voltage": 2, "ecd slow voltage": 3, "reference cavity": 4, "resonator fast v": 5, 
                "resonator slow v": 6, "aux output pd": 7, "etalon error": 8, "ecd error": 9, "ecd pd1": 10, "ecd pd2": 11, "input pd": 12, 
                "reference cavity pd": 13, "resonator error": 14, "etalon pd ac": 15, "output_pd": 16}
            -report
        Reply:
            -status = {0: "operation completed", 1: "operation failed"}
            -condition = {0: "task completed", 1: "task failed"}
        """
        
        task = {"transmission_id":[19],
                    "op":"monitor_a",
                    "parameters":
                    {"signal":signal
                    }
                }
        recv = self.send_message(task)
        return recv
    
    def monitor_b(self,signal): ## Apply monitor B
        """ This command switches the requested signal to monitor B output port.
        Command:
            -signal = {"etalon dither": 1, "etalon voltage": 2, "ecd slow voltage": 3, "reference cavity": 4, "resonator fast v": 5, 
                "resonator slow v": 6, "aux output pd": 7, "etalon error": 8, "ecd error": 9, "ecd pd1": 10, "ecd pd2": 11, "input pd": 12, 
                "reference cavity pd": 13, "resonator error": 14, "etalon pd ac": 15, "output_pd": 16}
            -report
        Reply:
            -status = {0: "operation completed", 1: "operation failed"}
            -condition = {0: "task completed", 1: "task failed"}
        """
        
        task = {"transmission_id":[20],
                    "op":"monitor_b",
                    "parameters":
                    {"signal":signal
                    }
                }
        recv = self.send_message(task)
        return recv
    
    def select_etalon_profile(self,profile):## Select Etalon Profile
        """ Select etalon profile.
        Command:
            -profile = {1: "profile 1", 2: "profile 2", 3: "profile 3", 4: "profile 4", 5: "profile 5", 6: "digital slow lock"}
        Reply:
            -status = {0: "operation completed", 1: "operation failed"}
            -current_profile = {1: "profile 1", 2: "profile 2", 3: "profile 3", 4: "profile 4", 5: "profile 5", 6: "digital slow lock"}
            -max_profile = ## I have no idea how to assign this?
            -frequency = float # Profile frequency defined in kHz.
            -report = {0: "task completed", 1: "task failed"}
        """
        
        task = {"transmission_id":[21],
                    "op":"select_profile",
                    "parameters":
                    {"profile":profile
                    }
                }
        recv = self.send_message(task)
        return recv
    
    def get_status(self):
        """ This command obtains the current system status
        Command:
            -None
        Reply:
            -status = {0: "operation completed", 1: "operation failed"}
            -wavelength = float # current wavelength in nm
            -temperature = float # current temperature in deg C
            -temperature_status = str # "on" or "off"
            -etalon_lock = {"off": "the lock is off", "on": "the lock is on", "debug": "the lock is in a debug condition",
                "error": "the lock is in error", "search": "the lock search algorithm is active", "low": "the lock is off due to low output"}
            -etalon_voltage = float # reading in volts
            -cavity_lock = {"off": "the lock is off", "on": "the lock is on", "debug": "the lock is in a debug condition",
                "error": "the lock is in error", "search": "the lock search algorithm is active", "low": "the lock is off due to low output"}
            -resonator_voltage = float # reading in volts
            -ecd_lock = "not fitted" or {"off": "the lock is off", "on": "the lock is on", "debug": "the lock is in a debug condition",
                "error": "the lock is in error", "search": "the lock search algorithm is active", "low": "the lock is off due to low output"}
            -ecd_voltage = "not fitted" or float # reading in volts
            -output_monitor = float # reading in volts
            -etalon_pd_dc = float # reading in volts
            -dither = str # "on" or "off"
            
        """
        
        task = {"transmission_id":[22],
                    "op":"get_status"
                }
        recv = self.send_message(task)
        return recv
        
    def get_alignment_status(self): ## Beam Alignment Status
        """ This command obtains the current beam alignment status
        Command:
            -None
        Reply:
            -condition = {
                        "not_fitted": "Beam alignment is not fitted to this system.", 
                        "manual": "Beam alignment is in manual mode", 
                        "automatic": "Beam alignment is in automatic mode", 
                        "hold": "Beam alignment is in hold mode."
                        }
            -x_alignment = float # 0-100, current X alignment (%). Center is 50.
            -y_alignment = float # 0-100, current Y alignment (%). Center is 50.
            -x_automatic = float # Automatic alignment X value from DSP.
            -y_automatic = float # Automatic alignment Y value from DSP.
            -quadrant = {
                        1: "DAC X, adjusting down", 
                        2: "DAC X, adjusting up", 
                        3: "DAC Y, adjusting down", 
                        4: "DAC Y, adjusting up", 
                        5: "Unknown"}
        """
        
        task = {"transmission_id":[23],
                    "op":"get_alignment_status"
                }
        recv = self.send_message(task)
        return recv
        
    def beam_alignment(self,mode): ## Beam Alignment Control
        """ This command controls the operation of the beam alignment
        Command:
            -mode = {"manual": 1, "automatic": 2, "stop": 3, "one shot": 4}
            -report
        Reply:
            -status = {0: "operation completed", 1: "operation failed, not fitted"}
            -report = {0: "task completed", 1: "task failed"}
        """
        
        task = {"transmission_id":[24],
                    "op":"beam_alignment",
                    "parameters":
                    {"mode":mode
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def beam_adjust_x(self,x):
        """ Adjusts the x alignment in beam alignment operations.
        Command:
            -x_value = float # X alignment percentage value, center = 50
        Reply:
            -status = {0: "operation completed", 1: "operation failed, not fitted", 2: "operation failed, value out of range", 3: "operation failed, not in manual mode."}
            -report = {0: "task completed", 1: "task failed"}
        """
        
        task = {"transmission_id":[25],
                    "op":"beam_adjust_x",
                    "parameters":
                    {"x_value":[x]
                    }
                }
        recv = self.send_message(task)
        return recv
    
    def beam_adjust_y(self,y): ## Beam Alignment, y Adjustment
        """ Adjusts the y alignment in beam alignment operations
        Command:
            -y_value = float # Y alignment percentage value, center = 50
        Reply:
            -status = {0: "operation completed", 1: "operation failed, not fitted", 2: "operation failed, value out of range", 3: "operation failed, not in manual mode."}
            -report = {0: "task completed", 1: "task failed"}
        """
    
        task = {"transmission_id":[26],
                    "op":"beam_adjust_y",
                    "parameters":
                    {"y_value":[y]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def scan_stitch_initialise(self,scan,start,stop,rate,units): ## TeraScan, Initialization
        """ This command initialises the TeraScan operations on Solstis
        Command:
            -scan = str # "coarse" (BRF-only, not available) or "medium" (BRF + Etalon tuning) or "fine" (BRF + Etalon + Resonator tuning) or "line" (Line narrow scan, BRF + etalon + cavity tuning)
            -start = float # 650 - 1100, Scan start position in nm
            -stop = float # 650 - 1100, Scan stop position in nm
            -rate = {"Medium scan, GHz": [100, 50, 20, 15, 10, 5, 2, 1],
                "Fine scan and line narrow scan, GHz": [20, 10, 5, 2, 1],
                "Fine scan and line narrow scan, MHz": [500, 200, 100, 50, 20, 10, 5, 2, 1]
                "Line narrow scan, KHz": [500, 200, 100, 50]}
            -units = ["GHz/s", ## medium, fine, and line narrow scans
                "MHZ/s", ## fine and line narrow scans only
                "kHz/s"] ## line narrow scans only
        Reply:
            -status = {0: "operation completed", 1: "start out of range", 2:"stop out of range", 3: "scan out of range", 4: "TeraScan not available"}
        """
        task = {"transmission_id":[27],
                    "op":"scan_stitch_initialise",
                    "parameters":
                    {"scan":scan,
                    "start":[start],
                    "stop":[stop],
                    "rate":[rate],
                    "units":units
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def scan_stitch_op(self,scan,operation): ## TeraScan, Operation
        """ This command controls the TeraScan operations on Solstis
        Command:
            -scan = str # "medium" [BRF + etalon tuning], "fine" [BRF + etalon + resonator tuning], "line" [BRF + etalon + cavity tuning]
            -operation = str # "start" or "stop"
            -report
        Reply:
            -status = {0: "operation completed", 1: "operation failed", 2: "TeraScan not available"}
            -report = {0: "task completed", 1: "task failed"}
        """
    
        task = {"transmission_id":[28],
                    "op":"scan_stitch_op",
                    "parameters":
                    {"scan":scan,
                    "operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def scan_stitch_status(self,scan): ## TeraScan, Status
        """ This command obtains the status of the TeraScan operations on Solstis
        Command:
            -scan = str # "medium", "fine", "line"
        Reply:
            -status = {0: "not active", 1: "in progress", 2: "TeraScan not available"}
            -current = float # 650 - 1100, current wavelength position in nm. Only given if Status = 1
            -start = float # 650 - 1100, scan start wavelength in nm. Only given if Status = 1
            -stop = float # 650 - 1100, scan stop wavelength in nm. Only given if Status = 1
            -operation = {0: "TeraScan is tuning to get the next scan wavelength", 1: "TeraScan is performing a scan"} 
        """
        
        task = {"transmission_id":[29],
                    "op":"scan_stitch_status",
                    "parameters":
                    {"scan":scan
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def scan_stitch_output(self,operation): ## TeraScan, Configure Wavelength Output
        """ TeraScan operations can be configured to transmit the current wavelength and 
        operation to a Client system while TeraScan is running. This command turns this 
        feature on or off. The message is generated at the beginning and end of each scan 
        stage and may also be generated during the scan.
        
        A sample wavelength transmission is defined below after the usual Command/Reply 
        pair. This is an unprompted TCP transmission which has no reply.

        Command:
            -operation = "start", "stop"
        Reply:
            -status = {0: "operation completed", 1: "operation failed", 2: "Unused. If you get this... Yer a wizard, 'arry!", 3: "TeraScan not available."}
        """
        
        task = {"transmission_id":[30],
                    "op":"scan_stitch_output",
                    "parameters":
                    {"operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv
        
        """
        The following commented transmission is a reply-only transmission, sent from an ICE_Bloc at each scan stage in the TeraScan.
        Instead of using scan_stitch_output, use terascan_output as described in the following function.
        """
        ## Wavelength transmission
        # operator: "scan_stitch_wavelength"
        # parameter 1 string: "wavelength"
        # parameter 1 value: wavelength in nm (700 - 1000 approx)
        # parameter 2 string: "activity"
        # parameter 2 value: "scanning" or "stitching" or "finished" or "repeat"
        # No reply defined. 
        
    
    
    def terascan_output(self,operation,delay,update,pause): ## TeraScan, Automatic Output
        """ The TeraScan Automatic Output command is an enhanced version of “TeraScan, 
        Configure Wavelength Output” described above. The original command is still 
        recognised by the package and operates as described above. The Automatic Output 
        command allows the user a greater precision of operation and its functions are 
        described below. Either of these commands is valid for a TeraScan but they should 
        not both be used during the same scan.
        
        The TeraScan Automatic Output command configures the system to generate TCP 
        messages during the TeraScan process. The generated messages are only transmitted
        during the scan process and nothing is generated when the laser is being tuned. Each 
        transmission contains a wavelength and a status word describing the current condition 
        of the scan. This command enables or disables this operation.
        
        TeraScan Automatic Output has the following operational characteristics:
             Generate a message at the beginning of each scan segment containing the 
            wavelength and a status string, “start”, “repeat” or “recover”. See Status String 
            below for a full explanation of these conditions. 
             Allow a programmable pause between the start transmission and the scan 
            segment beginning to scan.
             Generate a message at selectable points within each segment. This message 
            will contain the wavelength and the status string “scan”.
             Generate a message at the end of each scan segment containing the wavelength 
            and the status string “end”.
            
        Command:
            -operation = str #"start" or "stop"
            -delay = int #1 - 1000, delay in ms. 
            -update = int # 0 - 50. 0 = no output, 1 - 50 = output generated at specified tuning points
            -pause = str #"on" or "off"
        Reply:
            -status = {0:"operation completed", 1:"operation failed", 2:"delay period out of range", 3:"update step out of range", 4:"TeraScan not available"}
        """
        
        task = {"transmission_id":[31],
                    "op":"terascan_output",
                    "parameters":
                    {"operation":operation,
                    "delay":[delay],
                    "update":[update],
                    "pause":pause
                    }
                }
        recv = self.send_message(task)
        return recv
        
        """
        There's another transmission recorded in the TCP protocols below this one, but before the next function.
        I am not sure what it is for, or when it is called/sent, but I have recorded it below in comments.
        """
        ## automatic_output
        # parameter 1 string = "wavelength"
        # parameter 1 value = wavelength in nm (700 - 1000)
        # parameter 2 string = "status"
        # parameter 2 value = "start", "repeat", "recover", "scan", "end"
        
    def fast_scan_start(self,scan,width,time): ## Start Fast Scan
        """ This command allows the remote interface to use the fast scans similar to those on the 
        control page of the SolsTiS. There are 12 possible scan options which operate on the 
        Etalon, Reference Cavity, Resonator and ECD tuning controls. The currently tuned
        value is taken to be the centre of the scan and the command is called with a scan width 
        and time. The start point of the scan is (centre – (0.5 * scan width)). The end of the 
        scan is (centre + (0.5 * scan width)). The tuning output is ramped from the start 
        point to the end point in the time given.

        Command:
            -scan = {"etalon_continuous":"etalon", "etalon_singular":"etalon", "cavity_continuous":"reference cavity", "cavity_single":"reference cavity",
            "resonator_continuous":"resonator", "resonator_single":"resonator", "ecd_continuous":"ecd", "fringe_test": "reference cavity", "resonator_ramp":"resonator",
            "ecd_ramp":"ecd", "cavity_triangular":"reference cavity", "resonator_triangular":"resonator"}
            -width = {"etalon":250,"reference cavity":130, "resonator":30, "ecd":100} # Maximum scan width, per scan type
            -time = float #0.01 - 10000, ramp duration in seconds
            -report
        Reply:
            -status = {0:"successful, scan in progress", 1:"failed, scan width too great for current tuning position", 2:"failed, reference cavity not fitted", 3:"failed, erc not fitted", 4:"invalid scan type", 5:"time > 10000 seconds"}
            -report = {0:"task completed", 1:"task failed, reason TBD"}
        """
        
        task = {"transmission_id":[32],
                    "op":"fast_scan_start",
                    "parameters":
                    {"scan":scan,
                    "width":[width],
                    "time":[time]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def fast_scan_poll(self,scan): ## Poll Fast Scan
        """ This command polls fast scans which are started by command fast_scan_start (Start Fast Scan)
        
        Command:
            -scan = {"etalon_continuous":"etalon", "etalon_singular":"etalon", "cavity_continuous":"reference cavity", "cavity_single":"reference cavity",
            "resonator_continuous":"resonator", "resonator_single":"resonator", "ecd_continuous":"ecd", "fringe_test": "reference cavity", "resonator_ramp":"resonator",
            "ecd_ramp":"ecd", "cavity_triangular":"reference cavity", "resonator_triangular":"resonator"}
        Reply:
            -status = {0:"scan not in progress", 1:"scan in progress", 2:"reference cavity not fitted", 3:"external reference cavity not fitted", 4:"invalid scan type"}
            -tuner_value = float #current value of tuning control for the given scan
        """
        
        task = {"transmission_id":[33],
                    "op":"fast_scan_poll",
                    "parameters":
                    {"scan":scan
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def fast_scan_stop(self,scan): ## Stop Fast Scan
        """ Stop a fast scan, re-centre tuner.
        
        Command:
            -scan = {"etalon_continuous":"etalon", "etalon_singular":"etalon", "cavity_continuous":"reference cavity", "cavity_single":"reference cavity",
            "resonator_continuous":"resonator", "resonator_single":"resonator", "ecd_continuous":"ecd", "fringe_test": "reference cavity", "resonator_ramp":"resonator",
            "ecd_ramp":"ecd", "cavity_triangular":"reference cavity", "resonator_triangular":"resonator"}
            -report
        Reply:
            -status = {0:"operation completed", 1:"operation failed", 2:"reference cavity not fitted", 3:"ecd not fitted", 4:"invalid scan type"}
            -report = {0:"task completed", 1:"task failed, reason TBD"}
        """
        
        task = {"transmission_id":[34],
                    "op":"fast_scan_stop",
                    "parameters":
                    {"scan":scan
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def fast_scan_stop_nr(self,scan): ## Stop Fast Scan, No Return
        """ This command stops the fast scans which are started by command 3.30. The tuning 
        value is NOT returned to its start position. This command is not available for ECD 
        operations which always return to the tuner start position
        
        Command:
            -scan = {"etalon_continuous":"etalon", "etalon_singular":"etalon", "cavity_continuous":"reference cavity", "cavity_single":"reference cavity",
            "resonator_continuous":"resonator", "resonator_single":"resonator", "ecd_continuous":"ecd", "fringe_test": "reference cavity", "resonator_ramp":"resonator",
            "ecd_ramp":"ecd", "cavity_triangular":"reference cavity", "resonator_triangular":"resonator"}
            -report
        Reply:
            -status = {0:"operation completed", 1:"operation failed", 2:"reference cavity not fitted", 3:"Unused. If you get this... Yer a wizard, 'arry!", 4:"invalid scan type"}
            -report = {0:"task completed", 1:"task failed, reason TBD"}
        """
        
        task = {"transmission_id":[35],
                    "op":"fast_scan_stop_nr",
                    "parameters":
                    {"scan":scan
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def pba_reference(self,operation): ## PBA Reference
        """ This command controls the operation of the PBA reference.
        
        Command:
            -operation = {"start":0, "stop":1}
            -report
        Reply:
            -status = {0:"operation completed", 1:"operation failed, not fitted"}
            -report =  {0:"task completed", 1:"task failed"}
        """
        
        task = {"transmission_id":[36],
                    "op":"pba_reference",
                    "parameters":
                    {"operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def pba_reference_status(self): ## PBA Reference Status
        """ Get the status of the PBA reference.
        
        Command:
            -None
        Reply:
            -status = {"not_fitted":"Beam alignment is not fitted to this system", "off":"PBA reference is not running", "tuning":"The system is tuning to the reference wavelength", "optimising":"The system is optimising the PBA"}
            -x_alignment = float # 0 - 100, current X alignment, percentage value, center is 50.
            -y_alignment = float # 0 - 100, current Y alignment, percentage value, center is 50.
        """
        
        task = {"transmission_id":[37],
                    "op":"pba_reference_status"
                }
        recv = self.send_message(task)
        return recv
        
    def get_wavelength_range(self): ## Wavelength Range
        """ This command obtains information about the wavelength range of the Solstis.
        
        Command:
            -None
        Reply:
            -minimum_wavelength = float # Minimum wavelength SolsTiS can tune to in nanometers.
            -maximum_wavelength = float # Maximum wavelength SolsTiS can tune to in nanometers.
            -extended_zones = int # Number of extended zones in the SolsTiS wavelength table. A start and stop value for each zone
                                  # will be returned by this command. If the count is 0, there are no extended zones and no zone start
                                  # or zone stop wavelengths will be returned.
            -start_zone = float # This is the start wavelength of an extended zone in nanometers.
            -stop_zone = float # This is the stop wavelength of an extended zone in nanometers.
        """
        
        task = {"transmission_id":[38],
                    "op":"get_wavelength_range"
                }
        recv = self.send_message(task)
        return recv
        
    def terascan_continue(self): ## TeraScan, Continue
        """ This command instructs a paused TeraScan to continue with the next scan segment. 
        TeraScan will pause automatically at the start of each segment if the pause option is 
        enabled on the automatic output command (See 3.31 TeraScan, Automatic Output).

        Command:
            -None
        Reply:
            -status = {0:"operation completed", 1:"operation failed, TeraScan was not paused", 2:"TeraScan not available."}
        """
        
        task = {"transmission_id":[39],
                    "op":"terascan_continue"
                }
        recv = self.send_message(task)
        return recv
        
    def read_all_adc(self): ## Read All ADC Channels
        """ This command returns the value of all of the ADC channels in the Ice-Bloc.
        The system ADC values are read by the software approximately once per second, 
        usually faster. This command returns the set of values currently held in store. The 
        “report” field may be used to obtain the values from the next reading if required.
        
        Command:
            -report
        Reply:
            -status = {0:"operation completed}, 1:"operation failed"}
            -channel_count = int #18 or 38, depending on the number of ADC channels in this SolsTiS.
            -channel_n = str #name field from the ADC setup page for channel n
            -value_n = float # Current value for ADC channel n
            -units_n = str # Units field from ADC setup page for channel n
            -report = {0:"task completed", 1:"task failed"}
        """
        
        task = {"transmission_id":[40],
                    "op":"read_all_adc"
                }
        recv = self.send_message(task)
        return recv
        
    def set_wave_tolerance_m(self,tolerance): ## Set Wavelength Tuning Tolerance
        """ The maintenance of wavelength from V60 onwards has made tuning tolerance 
        redundant because tuning never ends. From V60 onwards this command sets a 
        threshold where the report from set_wave_m may be generated. This allows 
        users who may be working to a coarse tolerance to move on to the next task
        once the report is received.

        Command:
            -tolerance = float # Desired tolerance value. Depending on the meter, minimum tolerance varies. Maximum tolerance = 1.
        Reply:
            -status = {0:"operation successful", 1:"no link to wavelength meter or meter not configured", 2:"tolerance value out of range"}
        """
        
        task = {"transmission_id":[41],
                    "op":"set_wave_tolerance_m",
                    "parameters":
                    {"tolerance":[tolerance]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def set_wave_lock_tolerance_m(self,tolerance): ## Set Wavelength Lock Tolerance
        """ This command has become obsolete from V60 onwards. The concept of 
        wavelength locking to the wavelength meter has been removed and the Solstis 
        always maintains the current wavelength. This command has no effect and is 
        simply acknowledged with status 0.

        Command:
            -tolerance = float # Desired tolerance value. Depending on the meter, minimum tolerance varies. Maximum tolerance = 1.
        Reply:
            -status = {0:"operation successful", 1:"no link to wavelength meter or meter not configured", 2:"tolerance value out of range"}
        """
        
        task = {"transmission_id":[42],
                    "op":"set_wave_lock_tolerance_m",
                    "parameters":
                    {"tolerance":[tolerance]
                    }
                }
        recv = self.send_message(task)
        
        ### This command seems administrative, and like I shouldn't allow it to be used. Commenting it out for now, if it is ever necessary it can be used after uncommenting.
    # def digital_pid_control(self,operation): ## Digital PID Loop Control
        # """ This command may be used to control a digital PID operation on the Solstis. This PID 
        # is used to control the temperature of the fibre laser in an EMM system.
        # This command has been developed as part of a system which includes a complete 
        # Solstis laser. This command will be rejected when used in other situations.
        
        # Command:
            # -operation = str #"start" or "stop"
        # Reply:
            # -status = {0:"operation successful", 1:"command failed"}
        # """
        
        # task = {"transmission_id":[43],
                    # "op":"digital_pid_control",
                    # "parameters":
                    # {"operation":operation
                    # }
                # }
        # recv = self.send_message(task)
        # return recv
        
    def digital_pid_poll(self): ## Digital PID Loop Poll
        """ This command may be used to poll the status of a digital PID operation on the Solstis.

        This command has been developed as part of a system which includes a complete 
        Solstis laser. This command will be rejected when used in other situations.
        
        Command:
            -None
        Reply:
            -status = {0:"operation successful", 1:"command failed"}
            -loop_status = {0:"not initialised", 1:"running", 2:"initialised but not running"}
            -target_output = float # DAC value the PID loop has to maintain
            -current_output = float # current DAC value
        """
        
        task = {"transmission_id":[44],
                    "op":"digital_pid_poll"
                }
        recv = self.send_message(task)
        return recv
        
    def set_w_meter_channel(self,channel): ## Set Wavelength Meter Channel
        """ This command is used to set the channel on the wavelength meter connected to 
        Solstis. This is only required when a multi-channel wavelength meter is being used in 
        conjunction with a fibre switch. **Note**: We do use a multi-channel WM with fiber switch. 

        Command:
            -channel = int # 0 = single channel operation, 1 - 8 = set channel 1 - 8
            -recovery = int # 1 = reset the meter and proceed, 2 = wait for the meter to return to the channel, 3 = abandon the request
        Reply:
            -status = {0:"operation successful", 1:"command failed", 2:"channel out of range"}
        """
        task = {"transmission_id":[45],
                    "op":"set_w_meter_channel",
                    "parameters":
                    {"channel":[channel]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def lock_wave_m_fixed(self,operation): ## Lock Wavelength Fixed (Wavelength Meter)
        """ This command causes the given wavelength to become the maintained wavelength. 
        This command has been developed as part of a system which includes a complete 
        Solstis laser. This command will be rejected when used in other situations.

        Command:
            -operation = str #"on" or "off"
            -lock_wavelength = float # This value is not range checked and the developer should ensure that it is within 
                                     # the system capability. The value may be supplied as a float and its precision 
                                     # may be one decimal place greater than that of the wavelength meter. 
        Reply:
            -status = {0:"operation successful", 1:"no link to wavelength meter or no meter configured"}
        """
        
        task = {"transmission_id":[46],
                    "op":"lock_wave_m_fixed",
                    "parameters":
                    {"operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def gpio_output(self,channel,value): ## GPIO Output Command
        """ This command causes a GPIO signal to be output on Solstis.
        
        Command:
            -channel = int # GPIO channel number, 0 - 31
            -value = int # 0 or 1
            -report
        Reply:
            -status = {0:"operation successful", 1:"operation failed"}
            -report = {0:"operation successful", 1:"operation failed"}
            -channel = int # input channel
            -value = int # input value
        """
        
        task = {"transmission_id":[47],
                    "op":"gpio_output",
                    "parameters":
                    {"channel":[channel],
                    "value":[value]
                    }
                }
        recv = self.send_message(task)
        
    def dac_ramping(self,dac_channel,start_stop,ramping_mode,step_mode,target_output,ramp_rate,update_rate,step_size): ## DAC Ramping Command
        """ This command causes the DAC output on Solstis to be ramped to a given level.

        Command:
            -dac_channel = int # 0 - 31, DAC channel number
            -start_stop = {1:"Start", 2:"Stop, DAC remains at position"}
            -ramping_mode = {1:"No ramping", 2:"Ramp only if the target is higher than the current output.", 3:"Ramp only if the target is lower than the current output", 4:"Always ramp in either direction"}
            -step_mode = {0:"Use the ramp rate and the DSP will calculate the step size to achieve the update rate", 1:"use the step size given"}
            -target_output = float # This is the final oputput for the DAC and is specified in user units.
            -ramp_rate = float # DAC update rate specified in user units per second.
            -update_rate = float # The time required update in seconds.
            -step_size = float # Step size in user units
        Reply:
            -status = {0:"operation successful", 1:"operation failed"}
            -expected_time = float # the time it will take to complete the task in seconds.
        """
        
        task = {"transmission_id":[48],
                    "op":"dac_ramping",
                    "parameters":
                    {"dac_channel":[dac_channel],
                    "start_stop":start_stop,
                    "ramping_mode":ramping_mode,
                    "step_mode":step_mode,
                    "target_output":[target_output],
                    "ramp_rate":[ramp_rate],
                    "update_rate":[update_rate],
                    "step_size":[step_size]
                    }
                }
        recv = self.send_message(task)
        
    def dac_ramping_poll(self,dac_channel): ## DAC Ramping Poll
        """ This command reports the current status of a DAC ramping command

        Command:
            -dac_channel = int # 0 - 31, DAC channel number
        Reply:
            -status = {0:"operation successful", 1:"operation failed"}
            -dac_channel = int # 0 - 31, DAC channel number
            -ramping_active = {1:"Yes", 2:"No"}
            -current_output = float # Current DAC output expressed in user units
            -target_output = float # Target output expressed in user units
        """
        task = {"transmission_id":[49],
                    "op":"dac_ramping_poll",
                    "parameters":
                    {"dac_channel":[dac_channel]
                    }
                }
        recv = self.send_message(task)
        
    def digital_pot_output(self,channel,value): ## Digital Potentiometer Output Command
        """ This command causes a given values to be output to the selected digital potentiometer on Solstis.

        Command:
            -channel = int # 0 - 36, Digital Potentiometer channel number
            -value = int # 0 - 255
        Reply:
            -status = {0:"operation successful", 1:"operation failed"}
        """
        
        task = {"transmission_id":[50],
                    "op":"digital_pot_output",
                    "parameters":
                    {"channel":[channel],
                    "value":[value]
                    }
                }
        recv = self.send_message(task)
        
    def dac_output(self,channel,output_value): ## Digital to Analogue Output Command
        """ This command causes a given values to be output to the selected DAC on Solstis.
        
        Command:
            -channel = int # 0 - 30, Digital to Analogue Output channel number
            -output_value # The range of the output value varies according to the definition of the DAC.
        Reply:
            -status = {0:"operation successful", 1:"operation failed", 2:"output value out of range"}
            -channel = channel
        """
        
        task = {"transmission_id":[51],
                    "op":"dac_output",
                    "parameters":
                    {"channel":[channel],
                    "output_value":[output_value]
                    }
                }
        recv = self.send_message(task)
        
    def lock_mir_wavelength(self,operation,lock_wavelength): ## Lock MIR Wavelength Fixed (Wavelength Meter)
        """ This command locks a mid IR wavelength as the wavelength to be maintained in Solstis
        
        Command:
            -operation = str #"on" or "off"
            -lock_wavelength = float # 1100 - 2217 nm, The value may be supplied as a float and its 
                                     # precision may be one decimal place greater than that of the wavelength meter.
        Reply:
            -status = {0:"operation successful", 1:"no link to wavemeter or no meter configured", 2:"lock wavelength out of range"}
            -condition = 
            -voltage = 
        """
        
        task = {"transmission_id":[52],
                    "op":"lock_mir_wavelength",
                    "parameters":
                    {"operation":operation,
                    "lock_wavelength":[lock_wavelength]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def get_mir_wavelength(self): ## Get MIR Wavelengths (Wavelength Meter)
        """ This command gets the current three wavelength produced by MIR operations.

        Command:
            -None
        Reply:
            -ir_wavelength = float # Most recently read IR wavelength, SolsTiS output.
            -green_wavelength = float # Most recently read Verdi input. The green beam or mixing beam added to the IR beam to produce an MIR beam. ## Equinox wavelength?
            -mir_wavelength = float # Most recently used MIR wavelength
            -mir_active = {0:"Off", 1:"On"}
        """
        
        task = {"transmission_id":[53],
                    "op":"get_mir_wavelength"
                }
        recv = self.send_message(task)
        return recv
        
    def get_dac_tuning_values(self):
        """ The four DAC tuning values for Etalon, Resonator, Reference Cavity and ECD appear on 
        various pages within the Solstis product. These are expressed as a percentages, 0 –
        100%, and may be obtained by this command.

        Command:
            -None
        Reply:
            -etalon_tuner = float # DAC output value expressed as a percentage
            -resonator_tuner = float # DAC output value expressed as a percentage
            -cavity_tuner = float # DAC output value expressed as a percentage
            -ecd_tuner = float # DAC output value expressed as a percentage
        """
        
        task = {"transmission_id":[54],
                    "op":"get_dac_tuning_values"
                }
        recv = self.send_message(task)
        return recv
        
    def set_time(self,hour,minute,second,day,month,year): ## Set Time
        """ Set the clock in the Icebloc.
        
        Command:
            -hour, minute, second = int # 0-23, 0-59, 0-59. Ranges appropriate to a 24 hour clock. Midnight = 00:00:00
            -Day, Month, Year = int # 1-31, 1-12, 0-99. Ranges appropriate to 21st century, month and year checked for date field validity.
        Reply:
            -status = {0:"operation successful", 1:"operation failed"}
        """
        
        task = {"transmission_id":[55],
                    "op":"dac_output",
                    "parameters":
                    {"hour":[hour],
                    "minute":[minute],
                    "second":[second],
                    "day":[day],
                    "month":[month],
                    "year":[year]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def set_etalon_tuning_scan(self,operation): ## Etalon Scan Operation
        """ This command switches the Etalon Scan for wavelength tuning on or off.

        This operation scans the span of the Etalon tuner to find two wavelength peaks which 
        are near to the target wavelength. The peak nearest the centre of the Etalon tuning 
        DAC range is selected for further tuning

        Command:
            -operation = str #"on" or "off"
        Reply:
            -status = {0:"operation successful", 1:"operation failed"}
        """
        
        task = {"transmission_id":[56],
                    "op":"set_etalon_tuning_scan",
                    "parameters":
                    {"operation":operation
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def slow_wavelength_update(self,operation,p_const,i_const,interval): ## Slow Wavelength Update
        """ This command switches the Slow Wavelength Update on or off.

        If wavelength tuning has been running and is currently maintaining wavelength then it 
        is stopped so that the slow wavelength update can run in its place

        Command:
            -operation = str #"on" or "off"
            -p_constant, i_constant = float # PI tuning constants for the P and I of a PI tuning operation. The values range from 
                                            # 0 to 10 and are usually fractional. 0.7 and 0.02 are a pair commonly used in tuning operations.
            -interval = float # 0 - 100, time interval in seconds between wavelength checks. 
        Reply:
            -status = {0:"operation successful", 1:"operation failed"}
        """
        
        task = {"transmission_id":[57],
                    "op":"slow_wavelength_update",
                    "parameters":
                    {"operation":operation,
                    "p_const":[p_const],
                    "i_const":[i_const],
                    "interval":[interval]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def beam_maximising_3_axis(self,instance,run_mode,cont_mode,run_count,update_rate,power_drop,
                        dac_x_channel,dac_x_enable,dac_x_value,dac_x_step,dac_x_end_value,
                        dac_y_channel,dac_y_enable,dac_y_value,dac_y_step,dac_y_end_value,
                        dac_z_channel,dac_z_enable,dac_z_value,dac_z_step,dac_z_end_value,
                        adc_channel): ## 3-Axis Beam Maximising
        """ Runs the 3-Axis Beam Maximising Routine.
        
        Command:
            -Uhhhh 22 params, I'm not writing this out....
        Reply:
            -status = {0:"operation successful", 1:"operation failed"}
        """
        
        task = {"transmission_id":[58],
                    "op":"beam_maximising_3_axis",
                    "parameters":
                    {"instance":instance,
                    "run_mode":run_mode,
                    "cont_mode":cont_mode,
                    "run_count":run_count,
                    "update_rate":update_rate,
                    "power_drop":power_drop,
                    "dac_x_channel":dac_x_channel,
                    "dac_x_enable":dac_x_enable,
                    "dac_x_value":dac_x_value,
                    "dac_x_step":dac_x_step,
                    "dac_x_end_value":dac_x_end_value,
                    "dac_y_channel":dac_y_channel,
                    "dac_y_enable":dac_y_enable,
                    "dac_y_value":dac_y_value,
                    "dac_y_step":dac_y_step,
                    "dac_y_end_value":dac_y_end_value,
                    "dac_z_channel":dac_z_channel,
                    "dac_z_enable":dac_z_enable,
                    "dac_z_value":dac_z_value,
                    "dac_z_step":dac_z_step,
                    "dac_z_end_value":dac_z_end_value,
                    "adc_channel":adc_channel
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def beam_maximising_3_axis_status(self): ## 3-Axis Beam Maximising Status
        """ Gets the current status of the 3-Axis Beam Maximising routine.
        
        Command:
            -None
        Reply:
            -13 returned values. I hate everything.
            -status = {0:"operation successful", 1:"operation failed"}
            -reported_mode = {1:"manual", 2:"maximise", 3:"off and holding last values"}
            -quadrant_optimising = {1:"DAC X being adjusted, going down", 2:"DAC X being adjusted, going up", 3:"DAC Y being adjusted, going down", 4:"DAC Y being adjusted, going up", 5:"DAC Z being adjusted, going down", 6:"DAC Z being adjusted, going up", 7:"Unknown/Manual"}
            -algorithm_status = {0:"not optimising", 1:"OK, new maximum found", 2:"OK, current power is higher output than manual values", 3:"OK, current power is lower than manual values", 4:"Error, current power is below manual level, below limit"}
            -run_count = int 
            -dac_x_current_value = float
            -dac_x_optimised_value = float
            -dac_y_current_value = float
            -dac_y_optimised_value = float
            -dac_z_current_value = float
            -dac_z_optimised_value = float
            -adc_current_value = float
            -adc_optimised_value = float
        """
        
        task = {"transmission_id":[59],
                    "op":"beam_maximising_3_axis_status"
                }
        recv = self.send_message(task)
        return recv
        
    def set_system_variable(self,variable,condition): ## Set System Variable
        """ No Description Available
        Command:
            -variable = str #"maintain_wavelength" or "maintain_ecd"
            -condition = str #"on" or "off"
        Reply:
            -status = 
            
        """
        
        task = {"transmission_id":[60],
                    "op":"set_system_variable",
                    "parameters":
                    {"variable":variable,
                    "condition":condition
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def table_entry_info(self, wavelength):
        """ Retrieves the information about a specific wavelength entry in the table.
        Command:
            -None
        Reply:
            -status = 
            -condition = 
            -voltage = 
        """
        
        task = {"transmission_id":[61],
                    "op":"table_entry_info",
                    "parameters":
                    {"wavelength":[wavelength]
                    }
                }
        recv = self.send_message(task)
        return recv
        
    def system_info(self):
        """ Provides information on the connected hardware, and active software versions in this ICE_Bloc.
        The majority of this information is retrieved from the data stored in the EEPROM that can be configured
        from the Hardware Configuration page.
        Command:
            -None
        Reply:
            -status = 
            -condition = 
            -voltage = 
        """
        
        task = {"transmission_id":[62],
                    "op":"system_info"
                }
        recv = self.send_message(task)
        return recv
        
    def beam_alignment_configure(self,instance,dac_x_channel,dac_y_channel,adc_channel,beam_x_step_size,beam_y_step_size,
                                beam_x_value,beam_y_value,update_period,max_power_drop,continuous_mode,run_count):
        """ Modifies the setup for a specific beam alignment instance.
        Command:
            -None
        Reply:
            -status = 
            -condition = 
            -voltage = 
        """
        
        task = {"transmission_id":[63],
                    "op":"beam_alignment_configure",
                    "parameters":
                    {"instance":instance,
                    "dac_x_channel":dac_x_channel,
                    "dac_y_channel":dac_y_channel,
                    "adc_channel":adc_channel,
                    "beam_x_step_size":beam_x_step_size,
                    "beam_y_step_size":beam_y_step_size,
                    "beam_x_value":beam_x_value,
                    "beam_y_value":beam_y_value,
                    "update_period":update_period,
                    "max_power_drop":max_power_drop,
                    "continuous_mode":continuous_mode,
                    "run_count":run_count,
                    }
                }
        recv = self.send_message(task)
        return recv
    
    def close(self):
        self.laser.close()

"""
To ensure the Equinox, SFG, and DFG modules are all working as intended, go to the Network Settings page under the configure menu for the modules.
The user computer's static IP must be recorded and saved in one of the "Remote Interface" fields on the module. 
I advise always replacing the DFG on the equinox page (and simply disabling the connection on the DFG page).
DFG-Eq port: 49946
Eq-User Device port: 49956
DFG-User Device port: 49966
"""

class Equinox:
    """
    When operating the M-Squared Laser System through this class method, call functions via EquinoxObject.function(params).
    Please see the TCP/IP Protocols document for a full list of functions or find below.
    """
    
    def __init__(self,port=49946,host='192.168.1.225'):
        self.equinox = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # This initializes the socket with Address Family "INET" and type "SOCK_STREAM".
        self.equinox.connect((host,port)) # Connect to the socket with the given host and port information.
        # print(self.start_link())
    
    def _message(self,task):
        message = {"message":task}
        jsonMessage = json.dumps(message)
        return jsonMessage
    
    def read_message(self,message):
        """
        Command to decode the reply messages. Assumes that messages received use the following format:
        {"message":{"transmission_id":[id], "op":operation, "parameters":{param_name:param}}}
        """
        load = json.loads(message)
        return load['message']['parameters']
        
    def send_message(self,task):
        """
        Command to send the message through TCP protocols. Individual commands (see functions below) are
        structured to be in the appropriate dict format already. The private _message function called in this function
        transforms the task to JSON format, which is then sent to the ICE Bloc.
        Returned data will contain the system reply. Each function has it's own dictionary of replies, which are decoded
        in the command function.
        """
        message = self._message(task)
        #print(message)
        self.equinox.sendall(message.encode())
        data = self.read_message(self.equinox.recv(2048))
        return data
    
    def start_link(self,ip_address="192.168.1.108"): # This IP address is the client IP address for the user's computer.
        task = {"transmission_id":[900],
                "op":"start_link",
                "parameters":
                {"ip_address":ip_address}
                }
        recv = self.send_message(task)
        return recv
    
    def ping(self,text):
        """
        This command causes the receiving box to invert the case of the received text and 
        send it back.
        """
        task = {"transmission_id":[901],
                "op":"ping",
                "parameters":{
                    "text_in":text
                    }
                }
        recv = self.send_message(task)
        return recv
    
    def laser_control(self,operation):
        """
        This command instructs the Equinox to change the state of the laser. The user or ICE 
        Bloc issuing this command must poll the ‘laser_status’ command to retrieve the status 
        of the laser.
        Command:
            -operation = "warm_up" or "cool_down" or "start" or "stop"
        Reply:
            -operation = "warm_up" or "cool_down" or "start" or "stop"
            -status = {0:"command successfuly", 1:"command failed, operation in progress", 2:"command failed, laser already in requested state", 
                        3:"command failed, laser not warmed up", 4:["command failed, waveplate motor not referenced","command failed, laser emission active"], 5:"command failed, interlock open", 
                        6:"command failed, shutter open", 7:"command failed, external diode driver not accessible"}
        """
        task = {"transmission_id":[1],
                "op":"laser_control",
                "parameters":
                {"operation":operation}
                }
        recv = self.send_message(task)
        return recv

    def set_power(self,power):
        """
        This command requests a new set power for the laser. The laser must be fully on with the 
        shutter open in order to set the power. 
        Command:
            -power = float # power in watts
        Reply:
            -status = {0:"command successful", 1:"command failed, power out of range", 2:"command failed, laser not fully on", 3:"command failed, shutter not open"}
        """
        task = {"transmission_id":[2],
                "op":"set_power",
                "parameters":
                {"power":[power]}
                }
        recv = self.send_message(task)
        return recv
    
    def interlock_reset(self):
        """
        This command instructs the laser to reset the interlock latch. This must be done before 
        starting the laser if the interlock circuit is broken. 
        Command:
            -None
        Reply:
            -status = {0:"command successful", 1:"command failed"}
        """
        task = {"transmission_id":[3],
                "op":"interlock_reset"
                }
        recv = self.send_message(task)
        return recv

    def laser_status(self):
        """
        This command retrieves the status of the laser.
        Command:
            -None
        Reply:
            -emission_status = "off" or "delay" or "ramping" or "standby" or "on"
            -interlock_status = "latched_open" or "closed"
            -shutter_status = "closed" or "open" or "part_open" or "fault"
            -set_power = float # Current power value in watts
            -current_operation = "none" or "warm_up" or "cool_down" or "start" or "stop"
            -time_remaining = float # Time remaining for warmup or cooldown in seconds
            -warm_up_complete = "yes" or "no"
            -fault_condition = "none" or "over_current" or "over_volt" or "under_volt" or "interlock" or "shutter" or "temperature" or "pd"
            -diode_current = float # Diode current in amps
            -diode_voltage_a = float # Diode voltage A value in volts
            -diode_voltage_b = float # Diode voltage B value in volts
            -diode_isExternal = {0:"internal diode driver", 1:"external diode driver"}
            -external_temperature = float # External diode driver temperature in Celcius
            -photodiode_1 = float # photodiode 1 value
            -photodiode_2 = float # photodiode 2 value
            -photodiode_3 = float # photodiode 3 value
            -photodiode_4 = float # photodiode 4 value
            -photodiode_5 = float # photodiode 5 value
            -photodiode_6 = float # photodiode 6 value
            -temperature_1 = float # temperature 1 value in Celcius
            -temperature_2 = float # temperature 2 value in Celcius
            -temperature_3 = float # temperature 3 value in Celcius
            -temperature_4 = float # temperature 4 value in Celcius
            -temperature_5 = float # temperature 5 value in Celcius
            -temperature_6 = float # temperature 6 value in Celcius
            -tc4_1 = float # TC4 temperature 1 value in Celcius
            -tc4_2 = float # TC4 temperature 2 value in Celcius
            -tc4_3 = float # TC4 temperature 3 value in Celcius
            -tc4_4 = float # TC4 temperature 4 value in Celcius
            -diode_isExternal = {0:"internal diode driver", 1:"external diode driver"}
            -external_temperature = float # exxternal diode temperature in Celcius
            -waveplate_status = {0:"motor not initialized", 1:"stage not referenced", 2:"stage referenced", 3:"reference in progress"}
        """
        task = {"transmission_id":[4],
                "op":"laser_status"
                }
        recv = self.send_message(task)
        return recv
    
    def waveplate_prepare(self):
        """
        This command instructs the laser to initialize, prepare and reference the waveplate motor,
        which must be done before the laser can be started.
        Command:
            -None
        Reply:
            -status = {0:'command successful', 1:'command failed'}
        """
        task = {"transmission_id":[5],
                "op":"waveplate_prepare"
                }
        recv = self.send_message(task)
        return recv
    def close(self):
        self.equinox.close()
        
class SFG:
    """
    When operating the M-Squared Laser System through this class method, call functions via SFGObject.function(params).
    Please see the TCP/IP Protocols document for a full list of functions or find below.
    """  

    def __init__(self,port=39902,host="192.168.1.221"): ## Default: EMM-1950 (SFG)
        self.laser = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # This initializes the socket with Address Family "INET" and type "SOCK_STREAM".
        self.laser.connect((host,port)) # Connect to the socket with the given host and port information.

    def _message(self,task):
        message = {"message":task}
        jsonMessage = json.dumps(message)
        return jsonMessage

    def read_message(self,message):
        """
        Command to decode the reply messages. Assumes that messages received use the following format:
        {"message":{"transmission_id":[id], "op":operation, "parameters":{param_name:param}}}
        """
        load = json.loads(message)
        return load['message']['parameters']
        
    def send_message(self,task):
        """
        Command to send the message through TCP protocols. Individual commands (see functions below) are
        structured to be in the appropriate dict format already. The private _message function called in this function
        transforms the task to JSON format, which is then sent to the ICE Bloc.
        Returned data will contain the system reply. Each function has it's own dictionary of replies, which are decoded
        in the command function.
        """
        message = self._message(task)
        self.laser.sendall(message.encode())
        data = self.read_message(self.laser.recv(2048))
        return data
    
    def start_link(self,ip_address='192.168.1.108'): # This IP address is the client IP address for the user's computer.
        task = {"transmission_id":[900],
                "op":"start_link",
                "parameters":
                {"ip_address":ip_address}
                }
        recv = self.send_message(task)
        return recv
    
    def ping(self,text):
        """
        This command causes the receiving box to invert the case of the received text and 
        send it back.
        """
        task = {"transmission_id":[901],
                "op":"ping",
                "parameters":
                {"text_in":text}
                }
        recv = self.send_message(task)
        return recv
        
    def wavelength(self,beam,target):
        """
        This command changes the current wavelength of the laser.
        Command:
            -beam = "visible" or "infrared"
            -target = int # Target wavelength in nm
        Reply:
            -status = {0:"command successful", 1:"command failed, target wavelength out of range"}
            -report = {0:"wavelength tuning successful", 1:"wavelength tuning failed"}
        """
        task = {"transmission_id":[1],
                "op":"wavelength",
                "parameters":
                {"beam":beam,
                "target":target}
                }
        recv = self.send_message(task)
        return recv
        
    def wavelength_stop(self):
        """
        This command stops the current wavelength tuning operation of the laser
        Command:
            -None
        Reply:
            -status = {0:"command successful", 1:"command failed, no tuning in progress"}
            -report = {0:"wavelength tuning stop successful", 1:"wavelength tuning stop failed"}
        """
        task = {"transmission_id":[2],
                "op":"wavelength_stop"
                }
        recv = self.send_message(task)
        return recv
    
    def status(self):
        """
        This command retrieves the status of the laser.
        Command:
            -None
        Reply:
            -wavelength = float # Current wavelenght value
            -tuning = {"active":"Wavelength tuning in progress", "idle":"The system is not tuning"}
            -output_beam = float # Output beam monitor value
            -pump_beam = float # Pump beam monitor value
            -solstis_monitor = float # Solstis monitor value
            -emission = {"off":"Pump laser is off", "delay":"Pump laser in 5s delay before starting", "ramping":"Pump laser ramping up to set power", "on":"Pump laser on at set power", "not_available":"Pump laser control not fitted"}
            -shutter = {"closed":"Pump shutter is closed", "open":"Pump shutter is open", "not_available":"Pump laser control not fitted"}
            -uv_lock = {"off":"the lock is off", "on":"the lock is on", "debug":"the lock is in a debug condition", "error":"the lock operation is in error", "search":"the lock search algorithm is active", "low":"the lock is off due to low output"}
            -oven_status = {"active":"Normal operation", "optimising":"Optimizing position for maximum output", "stopping":"Shutting down for change over", "disabled":"Disabled (ready for change over), "starting":"Starting up after change over"}
            -fitted_oven = float # Fitted oven number
            -pba_status = {"off":"the PBA is off", "on":"the PBA is on"}
            -pba_reference = {"inactive":"Normal PBA operation", "auto":"Automatic PBA reference in progress", "manual":"Manual PBA reference in progress"}
        """
        task = {"transmission_id":[3],
                "op":"status"
                }
        recv = self.send_message(task)
        return recv
    
    def pba_control(self,action):
        """
        This command starts or stops the Solstis automatic PBA.
        Command:
            -action = "start" or "stop"
        Reply:
            -status = {0:"command successful", 1:"command failed"}
        """
        task = {"transmission_id":[4],
                "op":"pba_control",
                "parameters":
                {"action":action}
                }
        recv = self.send_message(task)
        return recv
    
    def pba_reference(self,action,solstis):
        """
        This command starts or stops the Solstis PBA reference process.
        Command:
            -action = "start" or "stop"
            -solstis = 1 or 2 # start action only
        Reply:
            -status = {0:"command successful",1:"command failed"}
        """
        task = {"transmission_id":[5],
                "op":"pba_reference",
                "parameters":
                {"action":action,
                "solstis":solstis}
                }
        recv = self.send_message(task)
        return recv
    
    def scan_stitch_initialise(self,scan,start,stop,rate,units):
        """
        This command initializes the TeraScan operations on EMM.
        Commands:
            -scan = {"medium":"BRF + etalon tuning in the visible range",
                    "fine":"BRF + etalon + resonator tuning in the visible range",
                    "ir_medium":"BRF + etalon tuning in the IR range",
                    "ir_fine":"BRF + etalon + resonator tuning in the IR range"}
            -start = 500 - 600 or 680 - 950 # Scan start position in the visible OR the IR ranges.
            -stop = 500 - 600 or 680 - 950 # Scan stop position in the visible OR the IR ranges.
            -rate = {"medium":{"GHz":['100','50','20','15','10','5','2','1']},
                    "fine":{"GHz":['20','10','5','2','1'],
                            "MHz":['500','200','100','50','20','10','5','2','1']}}
            -units = {"medium":["GHz"],"fine":["GHz","MHz"]}
        Reply:
            -status = {0:"operation completed",1:"start out of range",2:"stop out of range",3:"TeraScan not available"}
        """
        task = {"transmission_id":[6],
                "op":"pba_control",
                "parameters":
                {"scan":scan,
                "start":start,
                "stop":stop,
                "rate":rate,
                "units":units}
                }
        recv = self.send_message(task)
        return recv
        
    def scan_stitch_op(self,scan,operation):
        """
        This command controls the TeraScan operations on EMM.
        Commands:
            -scan = "medium" or "fine" or "ir_medium" or "ir_fine"
            -operation = "start" or "stop"
        Reply:
            -status = {0:"operation completed",1:"operation failed",2:"TeraScan not available"}
            -report = {0:"Task completed",1:"Task failed"}
        """
        task = {"transmission_id":[7],
                "op":"scan_stitch_op",
                "parameters":
                {"scan":scan,
                "operation":operation}
                }
        recv = self.send_message(task)
        return recv
    
    def scan_stitch_status(self,scan):
        """
        This command obtains the status of the TeraScan operations on EMM.
        Command:
            -scan = "medium" or "fine" or "ir_medium" or "ir_fine"
        Reply:
            -status = {0:"not active", 1:"in progress", 2:"TeraScan not available"}
            -current = float # Current wavelength. Only given if Status value is "in progress"
            -start = float # Start wavelength
            -stop = float # Stop wavelength
            -operation = {0:"TeraScan is tuning to get to the next scan wavelength", 1:"TeraScan is performing a scan"}
        """
        task = {"transmission_id":[8],
                "op":"scan_stitch_status",
                "parameters":
                {"scan":scan}
                }
        recv = self.send_message(task)
        return recv
    
    def terascan_output(self,operation,delay,update,pause):
        """
        The TeraScan Automatic Output command configures the system to generate TCP 
        messages during the TeraScan process. The generated messages are only transmitted 
        during the scan process and nothing is generated when the laser is being tuned. Each 
        transmission contains a wavelength and a status word describing the current condition 
        of the scan. This command enables or disables this operation.
        This command also enables or disables a pause operation which causes the TeraScan to 
        pause at the beginning of each scan phase. When paused, the generated output 
        command will show the software waiting at the “start” of the scan segment. The 
        controlling system is then in a position control other instrumentation before instructing 
        the scan to proceed. The continue command, see 3.10 below, is used to continue the 
        scan.
        Command:
            -operation = "start" or "stop"
            -delay = 0 - 1000 # scan delay after start transmission in 1/100s (0.01 - 10 s delay)
            -update = 0 - 1000 # frequency of messages during the scanning phase (0.01 - 10 s between messages)
            -pause = "on" or "off"
        """
        task = {"transmission_id":[9],
                "op":"terascan_output",
                "parameters":
                {"operation":operation,
                "delay":delay,
                "update":update,
                "pause":pause}
                }
        recv = self.send_message(task)
        return recv
    
    def terascan_continue(self):
        """
        This command instructs a paused TeraScan to continue with the next scan segment. 
        TeraScan will pause automatically at the start of each segment if the pause option is 
        enabled on the automatic output command (See 3.9 TeraScan, Automatic Output)
        Command:
            -None
        Reply:
            -status = {0:"operation completed", 1:"operation failed, TeraScan was not paused", 2:"TeraScan not available"}
        """
        task = {"transmission_id":[10],
                "op":"terascan_output"
                }
        recv = self.send_message(task)
        return recv
        
    def emm_read_all_adc(self):
        """
        This command reads back all the values of all ADCs from the EMM Ice Bloc
        Command:
            -None
        Reply:
            Many...
        """
        task = {"transmission_id":[9],
                "op":"emm_read_all_adc"
                }
        recv = self.send_message(task)
        return recv
    
    def close(self):
        self.laser.close()

class DFG:
    """
    When operating the M-Squared Laser System through this class method, call functions via SFGObject.function(params).
    Please see the TCP/IP Protocols document for a full list of functions or find below.
    """  

    def __init__(self,port=29922,host="192.168.1.221"): ## Default: EMM-1950 (SFG)
        self.laser = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # This initializes the socket with Address Family "INET" and type "SOCK_STREAM".
        self.laser.connect((host,port)) # Connect to the socket with the given host and port information.

    def _message(self,task):
        message = {"message":task}
        jsonMessage = json.dumps(message)
        return jsonMessage

    def read_message(self,message):
        """
        Command to decode the reply messages. Assumes that messages received use the following format:
        {"message":{"transmission_id":[id], "op":operation, "parameters":{param_name:param}}}
        """
        load = json.loads(message)
        return load['message']['parameters']
        
    def send_message(self,task):
        """
        Command to send the message through TCP protocols. Individual commands (see functions below) are
        structured to be in the appropriate dict format already. The private _message function called in this function
        transforms the task to JSON format, which is then sent to the ICE Bloc.
        Returned data will contain the system reply. Each function has it's own dictionary of replies, which are decoded
        in the command function.
        """
        message = self._message(task)
        self.laser.sendall(message.encode())
        data = self.read_message(self.laser.recv(2048))
        return data
    
    def start_link(self,ip_address='192.168.1.108'): # This IP address is the client IP address for the user's computer.
        task = {"transmission_id":[900],
                "op":"start_link",
                "parameters":
                {"ip_address":ip_address}
                }
        recv = self.send_message(task)
        return recv
    
    def ping(self,text):
        """
        This command causes the receiving box to invert the case of the received text and 
        send it back.
        """
        task = {"transmission_id":[901],
                "op":"ping",
                "parameters":
                {"text_in":text}
                }
        recv = self.send_message(task)
        return recv
        
    def wavelength(self,beam,target):
        """
        This command changes the current wavelength of the laser.
        Command:
            -beam = "visible" or "infrared"
            -target = int # Target wavelength in nm
        Reply:
            -status = {0:"command successful", 1:"command failed, target wavelength out of range"}
            -report = {0:"wavelength tuning successful", 1:"wavelength tuning failed"}
        """
        task = {"transmission_id":[1],
                "op":"wavelength",
                "parameters":
                {"beam":beam,
                "target":target}
                }
        recv = self.send_message(task)
        return recv
        
    def wavelength_stop(self):
        """
        This command stops the current wavelength tuning operation of the laser
        Command:
            -None
        Reply:
            -status = {0:"command successful", 1:"command failed, no tuning in progress"}
            -report = {0:"wavelength tuning stop successful", 1:"wavelength tuning stop failed"}
        """
        task = {"transmission_id":[2],
                "op":"wavelength_stop"
                }
        recv = self.send_message(task)
        return recv
    
    def status(self):
        """
        This command retrieves the status of the laser.
        Command:
            -None
        Reply:
            -wavelength = float # Current wavelenght value
            -tuning = {"active":"Wavelength tuning in progress", "idle":"The system is not tuning"}
            -output_beam = float # Output beam monitor value
            -pump_beam = float # Pump beam monitor value
            -solstis_monitor = float # Solstis monitor value
            -emission = {"off":"Pump laser is off", "delay":"Pump laser in 5s delay before starting", "ramping":"Pump laser ramping up to set power", "on":"Pump laser on at set power", "not_available":"Pump laser control not fitted"}
            -shutter = {"closed":"Pump shutter is closed", "open":"Pump shutter is open", "not_available":"Pump laser control not fitted"}
            -uv_lock = {"off":"the lock is off", "on":"the lock is on", "debug":"the lock is in a debug condition", "error":"the lock operation is in error", "search":"the lock search algorithm is active", "low":"the lock is off due to low output"}
            -oven_status = {"active":"Normal operation", "optimising":"Optimizing position for maximum output", "stopping":"Shutting down for change over", "disabled":"Disabled (ready for change over), "starting":"Starting up after change over"}
            -fitted_oven = float # Fitted oven number
            -pba_status = {"off":"the PBA is off", "on":"the PBA is on"}
            -pba_reference = {"inactive":"Normal PBA operation", "auto":"Automatic PBA reference in progress", "manual":"Manual PBA reference in progress"}
        """
        task = {"transmission_id":[3],
                "op":"status"
                }
        recv = self.send_message(task)
        return recv
    
    def laser_control(self,action):
        """
        This command starts or stops the pump laser.
        Command:
            -action = "on" or "off"
        Reply:
            -status = {0:"command successful",1:"command failed, pump laser control not fitted"}
        """
        task = {"transmission_id":[4],
                "op":"laser_control",
                "parameters":
                {"action":action}
                }
        recv = self.send_message(task)
        return recv
        
    def shutter_control(self,action):
        """
        This command opens or closes the pump laser shutter.
        Command:
            -action = "open" or "close"
        Reply:
            -status = {0:"command successful",1:"command failed, pump laser control not fitted"}
        """
        task = {"transmission_id":[5],
                "op":"shutter_control",
                "parameters":
                {"action":action}
                }
        recv = self.send_message(task)
        return recv
        
    def pba_control(self,action):
        """
        This command starts or stops the Solstis automatic PBA.
        Command:
            -action = "start" or "stop"
        Reply:
            -status = {0:"command successful", 1:"command failed"}
        """
        task = {"transmission_id":[6],
                "op":"pba_control",
                "parameters":
                {"action":action}
                }
        recv = self.send_message(task)
        return recv
    
    def pba_reference(self,action,solstis):
        """
        This command starts or stops the Solstis PBA reference process.
        Command:
            -action = "start" or "stop"
            -solstis = 1 or 2 # start action only
        Reply:
            -status = {0:"command successful",1:"command failed"}
        """
        task = {"transmission_id":[7],
                "op":"pba_reference",
                "parameters":
                {"action":action,
                "solstis":solstis}
                }
        recv = self.send_message(task)
        return recv
    
    def change_ppln(self):
        """
        This command shuts down the PPLN oven in order to be swapped out.
        Command:
            -None
        Reply:
            -status = {0:"command successful",1:"command failed}
        """
        task = {"transmission_id":[8],
                "op":"change_ppln"
                }
        recv = self.send_message(task)
        return recv
    
    def start_ppln(self,fitted_oven):
        """
        This command starts the PPLN oven after a change over.
        Command:
            -fitted_oven = 1 or 2 or 3 # Fitted oven ID
        Reply:
            -status = {0:"command successful", 1:"command failed"}
        """
        task = {"transmission_id":[9],
                "op":"start_ppln",
                "parameters":
                {"fitted_oven":fitted_oven}
                }
        recv = self.send_message(task)
        return recv

    def optimise_ppln(self):
        """
        This command optimizes the PPLN position for maximum output.
        Command:
            -None
        Reply:
            -status = {0:"command successful",1:"command failed"}
        """
        task = {"transmission_id":[9],
                "op":"optimise_ppln"
                }
        recv = self.send_message(task)
        return recv


## Example code demonstrating a basic solstis connection,
## reading out the current status of the laser system,
## and setting the wavelength of the system (assuming 
## a wavemeter is connected).
if __name__ == "__main__":
    import time    
    
    try:
        solstis = SolsTiS(port=39902,host='192.168.1.222') ## I have not implemented context manager for this, but it should be straightforward if desired.
        solstis.start_link()
        print(solstis.ping('Hello World'))
        status = solstis.get_status()
        for k,v in status.items():
            print(f'{k}:\t\t{v}')
        poll_wave = solstis.poll_wave_m() ## Returns a dictionary of values including status and wavelength
        
        if poll_wave['status'] == 1:
            print('No wavemeter connected.')
            raise Exception('No wavemeter connected. Use "poll_wave_t" command for tuning lookup table.')
        else:
            print(f'Starting wavelength: {poll_wave['current_wavelength'][0]}') ## Note the [0] index since integers are returned inside a list. 
            _ = solstis.set_wave_m(poll_wave['current_wavelength']+1)           ## Move wavelength by 1 nm
            time.sleep(0.5)
            wave2 = solstis.poll_wave_m()
            if wave2['status'] == 1:
                raise Exception('No wavemeter connected. Use "poll_wave_t" command for tuning lookup table.')
            else:
                print(f'Final wavelength: {poll_wave['current_wavelength'][0]}')
    except Exception as e:
        print(f'Something went wrong!\n\t{e}')
