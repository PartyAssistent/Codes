# Die example-Datei greift auf diesen Code zu #
# adapted from sandboxelectronics.com/?p=165 und von uns angepasst #

import time
import math
from MCP3008 import MCP3008 # Zugriff auf die Datei MCP3008

class MQ():

    ######################### Hardware-bezogene Macros #########################
    MQ_PIN                       = 0        # Analoger Input Channel des MQ 3
    RL_VALUE                     = 5        # Lastwiderstand in Kilo Ohm
    RO_CLEAN_AIR_FACTOR          = 60       # Sensor-Resistenz R0 des MQ-3 Sensors in ppm 
 
    ######################### Software-bezogene Macros #########################
    CALIBARAION_SAMPLE_TIMES     = 50       # 50 Samples werden in der Kalibrierungsphase gemessen
    CALIBRATION_SAMPLE_INTERVAL  = 500      # 500 Millisekunden Zeitintervall zwischen den Samples in der Kalibrierungsphase
    READ_SAMPLE_INTERVAL         = 50       # 50 Milisekunden Zeitintervall zwischen den Samples im Normalbetrieb define the time interval(in milisecond) between each samples in
    READ_SAMPLE_TIMES            = 5        # 5 Samples werden im Normalbetrieb gemessen
 
    ######################### Appplikations-bezogene Macros ######################
    GAS_Alcohol                  = 0

    def __init__(self, Ro=60, analogPin=0):
        self.Ro = Ro
        self.MQ_PIN = analogPin
        self.adc = MCP3008()
        
        self.AlcoholCurve = [-1.0,0.36,-0.64]   # Entnahme der Daten aus dem Data Sheet des MQ 3 Gassensors: Mithilfe von 2 Punkten aus der Kurve wird eine Linie bestimmt welche ähnlich der Originalkurve ist: data format:{ x, y, slope}
                                            # Bestimmung der Werte mithilfe der Fig.3 des Data Sheet typical sensitivity chracteristics 
                                            # Ablesen der Werte P1 und P2: P1(X=0.1, Y=2.3) P2(X=10, Y=0.12)
                                            # Errechnung der Steigung = -0.64
                                            # (log10(0.12)-log10(2.3))/log10(10)-log10(0.1)
                                            # Mit der Steigung und dem gezogenen Logarithmus aus P1 werden X=-1.0, Y=0.36 errechnet
                                            
        print("Calibrating...")
        self.Ro = self.MQCalibration(self.MQ_PIN)
        print("Calibration is done...\n")
        print("Ro=%f kohm" % self.Ro)
    
    
    def MQPercentage(self):
        val = {}
        read = self.MQRead(self.MQ_PIN)
        val["GAS_Alcohol"]  = self.MQGetGasPercentage(read/self.Ro, self.GAS_Alcohol)
        return val
        
    ######################### MQResistanceCalculation #########################
    # Input:   raw_adc - raw value read from adc, which represents the voltage
    # Output:  the calculated sensor resistance
    # Remarks: The sensor and the load resistor forms a voltage divider. Given the voltage
    #          across the load resistor and its resistance, the resistance of the sensor
    #          could be derived.
    ############################################################################ 
    def MQResistanceCalculation(self, raw_adc):
        return float(self.RL_VALUE*(1023.0-raw_adc)/float(raw_adc));
     
     
    ######################### MQCalibration ####################################
    # Input:   mq_pin - analog channel
    # Output:  Ro of the sensor
    # Remarks: This function assumes that the sensor is in clean air. It use  
    #          MQResistanceCalculation to calculates the sensor resistance in clean air 
    #          and then divides it with RO_CLEAN_AIR_FACTOR. RO_CLEAN_AIR_FACTOR is about 
    #          10, which differs slightly between different sensors.
    ############################################################################ 
    def MQCalibration(self, mq_pin):
        val = 0.0
        for i in range(self.CALIBARAION_SAMPLE_TIMES):          # take multiple samples
            val += self.MQResistanceCalculation(self.adc.read(mq_pin))
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL/1000.0)
            
        val = val/self.CALIBARAION_SAMPLE_TIMES                 # calculate the average value

        val = val/self.RO_CLEAN_AIR_FACTOR                      # divided by RO_CLEAN_AIR_FACTOR yields the Ro 
                                                                # according to the chart in the datasheet 

        return val;
      
      
    #########################  MQRead ##########################################
    # Input:   mq_pin - analog channel
    # Output:  Rs of the sensor
    # Remarks: This function use MQResistanceCalculation to caculate the sensor resistenc (Rs).
    #          The Rs changes as the sensor is in the different consentration of the target
    #          gas. The sample times and the time interval between samples could be configured
    #          by changing the definition of the macros.
    ############################################################################ 
    def MQRead(self, mq_pin):
        rs = 0.0

        for i in range(self.READ_SAMPLE_TIMES):
            rs += self.MQResistanceCalculation(self.adc.read(mq_pin))
            time.sleep(self.READ_SAMPLE_INTERVAL/1000.0)

        rs = rs/self.READ_SAMPLE_TIMES

        return rs
     
    #########################  MQGetGasPercentage ##############################
    # Input:   rs_ro_ratio - Rs divided by Ro
    #          gas_id      - target gas type
    # Output:  ppm of the target gas
    # Remarks: This function passes different curves to the MQGetPercentage function which 
    #          calculates the ppm (parts per million) of the target gas.
    ############################################################################ 
    def MQGetGasPercentage(self, rs_ro_ratio, gas_id):
        if ( gas_id == self.GAS_Alcohol ):
            return self.MQGetPercentage(rs_ro_ratio, self.AlcoholCurve)
        return 0
     
    #########################  MQGetPercentage #################################
    # Input:   rs_ro_ratio - Rs divided by Ro
    #          pcurve      - pointer to the curve of the target gas
    # Output:  ppm of the target gas
    # Remarks: By using the slope and a point of the line. The x(logarithmic value of ppm) 
    #          of the line could be derived if y(rs_ro_ratio) is provided. As it is a 
    #          logarithmic coordinate, power of 10 is used to convert the result to non-logarithmic 
    #          value.
    ############################################################################ 
    def MQGetPercentage(self, rs_ro_ratio, pcurve):
        return (math.pow(10,( ((math.log(rs_ro_ratio)-pcurve[1])/ pcurve[2]) + pcurve[0])))
