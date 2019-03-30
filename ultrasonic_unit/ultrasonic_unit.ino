
#define RESET_ALARM_COMMAND "RESET\n"
#define RESET_AND_MEASURE_COMMAND "RESET_AND_MEASURE\n"
//MAIN FILE

bool alarm_status = 0;
String hub_response = "";

bool debug = 0;

void react_to_hub_response(String response){

    Serial.print("Response = '");
    Serial.print(response);
    Serial.println("'");
    
    Serial.print("COMMAND = '");
    Serial.print(RESET_ALARM_COMMAND);
    Serial.println("'");
    if (response == RESET_ALARM_COMMAND){
        alarm_status = 0;
    }
    else if (response == RESET_AND_MEASURE_COMMAND){
        alarm_status = 0;
        set_initial_value();
    }
}


void setup() {
    setup_connection();
    ultrasonic_setup();
}

void loop() {

    if (debug){
        from_bluetooth_to_serial();
    }
    else{    
        if (get_state()){
            alarm_status = check_alarm();
    
            while (alarm_status){
                get_state();
                ble_send_alarm();
                delay(10);
    
                hub_response = ble_listen();
                react_to_hub_response(hub_response);
                delay(1500);
            }
        }
    
        delay(250);
    }
}
