#include <SPI.h>
#include <Wire.h>
#include "SD.h"
#include "RTClib.h"

// Number of thermocouple inputs -- data headers at end of 
// setup() must be changed manually
#define thermnum 	5

File logfile;

// mills b/w entries
int log_interval = 1000;

// create new file name
String filename = "00_DATA.CSV";

// Thermocouple Analog Input Pins
#define therm1		A0
#define therm2      A1
#define therm3		A2
#define therm4		A3
#define therm5 		A6

// Define RTC object
RTC_DS1307 RTC;

// for microSD, use digital pin 10 for SD cs line
#define chipSelect  10

// logging file
//File logfile;

void error(char *str) {
  while (1);
}

// gives the 2 digit hour/min/sec given a now() input
String get2digit(int n) {
  return n < 10 ? "0" + String(n, DEC) : String(n, DEC);
}

// sets the RTC based on XBee data
void xbeeWriteSettings(){

  int day = Serial.readStringUntil(',').toInt();
  int month = Serial.readStringUntil(',').toInt();
  int year = Serial.readStringUntil(',').toInt();
  int hour = Serial.readStringUntil(',').toInt();
  int minute = Serial.readStringUntil(',').toInt();
  int second = Serial.readStringUntil(',').toInt();
  log_interval = Serial.readStringUntil(',').toInt();
  
  
  RTC.adjust(DateTime(year, month, day, hour, minute, second));
}

// callback function for file timestamps
void dateTime(uint16_t* date, uint16_t* time) {
  DateTime now = RTC.now();
  
  // return date using FAT_DATE macro to format fields
  *date = FAT_DATE(now.year(), now.month(), now.day());

  // return time using FAT_TIME macro to format fields
  *time = FAT_TIME(now.hour(), now.minute(), now.second());
}

void setup() {
  Serial.begin(9600);
  
  // ensure default chip select pin is set to output
  pinMode(chipSelect, OUTPUT);

  Wire.begin();

  RTC.begin();

  if(!RTC.isrunning()){
	while (1);
  }
  
  // when the 'n' character is recieved, set the date, time, and loop delay
  while(Serial.read() != 'n'){}
  xbeeWriteSettings();

  // set SD file date and time with the callback function
  SdFile::dateTimeCallback(dateTime);

  // see if the card is present and can be initialized
  if (!SD.begin(chipSelect)) {
    return;
  }

  // this loop will check if the file you are creating already exists
  // then will increment the "00" until it finds a file name that DNE
  for (uint8_t i = 0; i < 100; i++) {
    filename[0] = i / 10 + '0';
    filename[1] = i % 10 + '0';
    if (!SD.exists(filename)) {
      // only open a new file if it doesnt exist
      logfile = SD.open(filename, FILE_WRITE);
      break;
    }
  }

  if (SD.exists(filename)) {
  }
  else {
    while (1);
  }

  // Send data headings to SD logfile and XBee 
  logfile.println("Time,Temp1,Temp2,Temp3,Temp4,Temp5,");//+year+"/"+month+"/"+day);
  logfile.close();
}

void loop() {  

  // if the LCA script is ran again, re-update the settings
  if(Serial.read() == 'n'){
    xbeeWriteSettings();
  }
  
  logfile = SD.open(filename, FILE_WRITE);
  DateTime now;

  // delay for amount of time wanted b/w readings
  delay((log_interval - 1) - (millis() % log_interval));

  // fetch the time
  now = RTC.now();
  // store time
  String ho = get2digit(now.hour());
  String mi = get2digit(now.minute());
  String se = get2digit(now.second());

  // Send time to SD logfile
  logfile.print(ho);
  logfile.print(":");
  logfile.print(mi);
  logfile.print(":");
  logfile.print(se);
  logfile.print(", ");

  // Read thermocouple analog voltages
  int thermanalog[5];
  thermanalog[0] = analogRead(therm1);
  thermanalog[1] = analogRead(therm2);
  thermanalog[2] = analogRead(therm3);
  thermanalog[3] = analogRead(therm4);
  thermanalog[4] = analogRead(therm5);
    
  double thermtemp[5];
  
  // Calculate the temperature values
  for(int i=0; i<5; i++){
	  double thermv_temp = (thermanalog[i] / 1023.0) * 5.0;
	  thermv_temp = ((thermv_temp - 1.2392)*1000) - 22; 
    
	  thermtemp[i] = (-0.17974) + (0.20855 * thermv_temp) + (-5.1041*pow(10, -5)*pow(thermv_temp,2)) + 
			             (5.1153*pow(10, -8)*pow(thermv_temp, 3)) + (-4.8922*pow(10, -11)*pow(thermv_temp, 4)) + 
		               (2.3402*pow(10, -14)*pow(thermv_temp, 5)) + (-4.1036*pow(10, -18)*pow(thermv_temp, 6));
  }
  
  for(int i=0; i<5; i++){
	  logfile.print(thermtemp[i]);
	  logfile.print(", ");
  }
  logfile.println();
  logfile.close();
  
  for(int i=0; i<5; i++){
	  Serial.print(thermanalog[i]);
	  Serial.print(' ');
  }
  Serial.println();
}
