##### Dieser Code wird mit dem Autostart ausgeführt. #####

from mq import * ###### Es wird auf die Datei "mq" zugegriffen #####
import sys, time

try:
    print("Press CTRL+C to abort.")  ##### Mit dem Befehl CTRL+C kann die Kalibrierung abgebrochen werden #####
    
    mq = MQ();
    while True:
        perc = mq.MQPercentage()
        sys.stdout.write("\r")
        sys.stdout.write("\033[K")
        sys.stdout.write("GAS_Alcohol: %g ppm" % (perc["GAS_Alcohol"]))
        sys.stdout.flush()
        time.sleep(0.1)
        promille=perc% 1000
    print(promille) ###### Der Promillewert wird in ppm ausgegeben #####

    # Umrechnung ppm (parts per million) in promille: 1% promille entspricht 1000 ppm
    promille = (math.pow(10,( ((math.log(rs_ro_ratio)-pcurve[1])/ pcurve[2]) + pcurve[0])))/1000
    print(promille)

    file = open("sensor_resultat.txt")
    file.write(promille)

except:
    print("\nAbort by user") ##### Wenn die Kalibrierung des Sensors beendet ist, endet die Ausführung des Codes #####