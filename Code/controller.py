#Harsh choudhary
import json,conf,time
from boltiot import Sms,Bolt

#set the thresholds for min_intensity below which the light must be turned on
min_intensity= 50

#set up the Bolt object and Sms instance
mybolt=Bolt(conf.bolt_api_key,conf.bolt_device_id)
mybolt_sms_test=Bolt("fhfjhjgkjhk",conf.bolt_device_id)
sms=Sms(conf.account_sid,conf.auth_token,conf.to_number,conf.from_number)
led_on=False
prev_intensity=-1
limit=10    #this is the expected increase in intensity due to LED light
#we have to tune limit properly

while True:
    #get the sensor value
    #the pin is A0
    reading=mybolt.analogRead('A0')
    data=json.loads(reading)
    print(data)
    try:
        sensor_value=int(data['value'])
        #test to see if the light intensity is less than threshold
        if(sensor_value<min_intensity):
            #thus switch on the LED
            print("Must switch LED on")
            if(not led_on):
                #if the led is already on then we can not help the situation
                #trying to switch the LED on
                print("Led is previously off")
                #command=mybolt_sms_test.digitalWrite('0','HIGH')
                command=mybolt.digitalWrite('0','HIGH')
                print(command)
                command_data=json.loads(command)
                if(command_data['success']==0):
                    print("Could not switch the LED ON")
                    #send sms to the owner
                    message_response=sms.send_sms("There is some defect in LED or system. It is dark. Replace the LED")
                    print(message_response)
                else:
                    #led has been switched on
                    prev_intensity=sensor_value
                    led_on=True    
        else:
            #the environment is not dark, so if the LED is ON, switch it off
            #it does no harm to switch off the LED even if it is off
            #but we wish to inform the house owner if despite our attempt LED could not be turned off
            #the owner may then manually turn off the LED
            if(led_on):        
                    #if prev_intensity is -1 then led_on must be false itself
                    #when led_on is set True, prev_intensity can not be -1 as it is also updated together
                if(sensor_value-prev_intensity>limit):
                    #only in this case switch off the LED
                    #because otherwise the increase in intensity due to the LED causes the sensor to detect more light and turn LED off
                    #which would then make LDR detect low light
                    #this leads to looping
                    command=mybolt.digitalWrite('0','LOW')
                    print(command)
                    command_data=json.loads(command)
                    if(command_data["success"]==0):
                        print("Will try to switch LED off a minute later")
                        #inform the owner
                        message_response=sms.send_sms("There is some defect in system. The LED needs to be turned off.")
                        print(message_response)
                    else:
                        led_on=False
            
    except:
        print("Can't read sensor data")

    time.sleep(60)
            
            
