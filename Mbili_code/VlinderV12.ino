/* ------- V L I N D E R ---------*/
/* 
 *  Version 12:
 *  removed code for storage on SD card
 *  
 *  Version 10 & 11 : temporarily test versions , not used
 *  
 *  Version 9:
 *  added check on return value of send() command
 *  
 *  Version 8:
 *  added if case to sendPayload command
 *  
 *  Version 7:
 *  changed RainVolume to direct reading of Davis Rain value
 *  conversion of Rain to RainToDay will be done on server side in Python
 *  
 *  Version 6:
 *  added continuous trying op modemsetup
 *  added all device codes and tokens
 *  
 *  Version 5: 
 *  conversion of RainRate and WindGust from Davis unit
 *  changed RainToDay calculation
 *  added modem reset if connect fails
 *  
 *  TO DO : transmit new values to ATT e save on SD
 * 
 *  Version 4:
 *  added green led for normal operation
 *  added DEBUGstream during INIT loop
 *  added average wind direction via array
 *  
 *  Version 3 : 
 *  added RainToDay value
 *  send to vlinder ground
 *  
*/

/*====================== I N C L U D E S =========================*/

#include <math.h>
#include <Wire.h>
#include "Sodaq_DS3231.h"      //RTC of the MBili
#include <Adafruit_BME280.h>   //BME280 atmosphere sensor
#include "ATT_NBIOT.h"         //AllThingsTalk Narrow Band Internet of Things

/*======================== D E F I N E S ==========================*/

#define DEBUG_STREAM Serial    // for testing DEBUG_STREAM is coupled to Serial0 for USB to PC
#define MODEM_STREAM Serial1   // rename serial port1 to MODEM_STREAM for NbIoT
#define DAVIS_STREAM Serial    // serial port 0 is for comm to Davis ISS
#define MODEM_ON_OFF_PIN 23
#define CBOR                   // Select your preferred method of sending data
#define DELAY_TIME 50
/*====================== C O N S T A N T S  =======================*/

const int SD_SS_PIN = 11;      //SD card ChipSelect is pin D11 

/*=============== ATT DEVICE SETUP ================================*/
/* uncomment the correct station number */
//ATT_NBIOT device("BI4qcac5ECy64p4vRSPESpxt","vlinderugent:4Nn5HT1IAWGOW1VeVoycGoZVF8FAnzQUlj2ajpj");    // Vlinder 00 TestUnit
//ATT_NBIOT device("jvy7zdAPZ5ymI2hydh6tvnmm","vlinderugent:4KVIZV1STjWLW1VeVsH5ofcnC4DnQ1aIWH0Trj7");    // Vlinder 01 Melle
//ATT_NBIOT device("zZ6ZeSg11dJ5zp5GrNwNck9A","vlinderugent:4N2X5D6PQaPNW1VeVq9tsQppIoOs2xQusxOhaP0");    // Vlinder 02 Gent
//ATT_NBIOT device("VDwYVFKNaGF0YpQtM4xe3Ic5","vlinderugent:4P8yYyQpezirK0ByXzypy3Dm66xOnR3RI1ZpWk55");   // Vlinder 03 Turnhout
//ATT_NBIOT device("vqYF3lib7K3re0Zc38ZCzlom","vlinderugent:4HSHr09JuWd6W1VeVq18PlzPJoZESRkYnRcRcYC");    // Vlinder 04 Turnhout
//ATT_NBIOT device("2kfOFUtZ5wZEEpM6xbL42aFM","vlinderugent:4LpIRtijbms0W1VeVpD4UFKKgdvyvDasAxOrnML");    // Vlinder 05 Gent
//ATT_NBIOT device("0xwg6AsDvbnxXzB4S3c2BRyJ","vlinderugent:4H1SYHH6KQ5ZW1VeVyb6ncockffgMvLjzb0BjBy0");   // Vlinder 06 Mechelen
//ATT_NBIOT device("3hG2KPxxvlPVDjDIlEkbS7A5","vlinderugent:4OORze7vs13IG0lqFufyUcLB3MEKdjBWyqlskdN1");   // Vlinder 07 Mechelen
//ATT_NBIOT device("h2Nl284RotYblunrLM8m6KtO","vlinderugent:4KTLzZE98aaPG0lqFy55ToA5HPxxyswxKcxOs6O0");   // Vlinder 08 Mechelen
//ATT_NBIOT device("hA49FTkzXFZBSPq1cu6l4J5b","vlinderugent:4LWKPvlF6yZNG0lqFySTsIiG7XcsyZFOCawQ3yX0");   // Vlinder 09 Aalst
//ATT_NBIOT device("11eLa6DbyiHBWFT1FxHzTMII","vlinderugent:4RHFXyROhYmNG0lqFyyj5CUU7PNxTNNyuLzuCpW4");   // Vlinder 10 Aalst
//ATT_NBIOT device("SMivapZavheUAoe0thH2d22U","vlinderugent:4TPyabYfVvBDG0lqFzhlyLzBf9o2xxxKELlpjVU0");   // Vlinder 11 Antwerpen
//ATT_NBIOT device("RyLeKizFOca8R95PJ9Ed9MPQ","vlinderugent:4NVGaMu7wz5yu0Nw7zT1or0JAr1QRFShSrdYyx10");   // Vlinder 12 Antwerpen
//ATT_NBIOT device("ezxlxqTCtJb6ChsNwO3GwAe8","vlinderugent:4UkqrTPkvhvuW1VeVqKdjE7y7N1t2O82l79BexA");    // Vlinder 13 Antwerpen
//ATT_NBIOT device("QDpOI8z0Avo55bojIzbom6l5","vlinderugent:4SmacM87DOx1W1VeVyeytDM3WHNl9yafcCVOvr11");   // Vlinder 14 Asse
//ATT_NBIOT device("iASUcbCWYglQzIdyQnALsTTT","vlinderugent:4HeFgQsrB55VW1VeVsrsxpZDIrzzNwlvKaSRSMH");    // Vlinder 15 Asse
//ATT_NBIOT device("DOo1XWMfhmleI0M9jlkOf1Wt","vlinderugent:4SnyhFQgtOe5G0lqFuSn7l9zLu5G7TJuC42pYeN");    // Vlinder 16 Beveren
//ATT_NBIOT device("eTuhBpgua9VVEqANPehNrR7g","vlinderugent:4Qzh3I23Re88m0lqFwzryIi4x74bzPysRziXnyoQ");   // Vlinder 17 Bree
//ATT_NBIOT device("Tw2SbKEtwIHD5OVf23zfKvfO","vlinderugent:4K5NFyWlQAkeG0lqFzc9bBVkICuOrCOaGUVBe9c");    // Vlinder 18 Bree
//ATT_NBIOT device("xgRUxj1N6DiRKzekQqI4Z5Ns","vlinderugent:4U3fCvwoP9sUW1VeVnmDfOaVnWGE4tZx6JZAn60");    // Vlinder 19 Brussel
//ATT_NBIOT device("Ziocm4OqUjrp7W9988artyfN","vlinderugent:4JlPsqIksuYDW1VeVzvMEiLoGAr6V2S3lJlMTzq");    // Vlinder 20 Brussel
//ATT_NBIOT device("Do5lLMfezIdmUCzzsE0IwIbE","vlinderugent:4TvJFjkXlO2MW1VeVzYr3rLuqmskx3WezMDezUr1");   // Vlinder 21 De Haan
//ATT_NBIOT device("WviZBVI37BRGQdtd0BFgBm7h","vlinderugent:4PGIdI1M027kW1VeVrexFpq8I0vMSF1koBNhrdD");    // Vlinder 22 Diksmuide
//ATT_NBIOT device("7u5R4nnIY5QmgbeBablX7PCd","vlinderugent:4TH79w2l6oMjW1VeVymI4zpqMk1dchDumA091Uq");    // Vlinder 23 Eeklo
//ATT_NBIOT device("mmcaGqeSebmJIAOPsOfZuCs5","vlinderugent:4JAoN522C0l1W1VeVmfVzRyu0hbtZUFli2NUmOU");    // Vlinder 24 Eeklo
//ATT_NBIOT device("wjNeGPl3OhXCsIfsIuLjKVRd","vlinderugent:4MOd2OTamDyAm0lqFy0gycLAKCC3c813aAUjUYO0");   // Vlinder 25 Evergem
//ATT_NBIOT device("aIbZHX6cZzv4DQbMPS5MrM57","vlinderugent:4VqzJZzNWoAc80Nw7zLZFBzEAJ20JGlSzT5DE0C1");   // Vlinder 26 Geel
//ATT_NBIOT device("ItzXCMYUzi31xyiEZpLxB7ef","vlinderugent:4VZaJz7QwENRG0lqFw9jSzUwPYyGuSsaGJZFKUg1");   // Vlinder 27 Gent
//ATT_NBIOT device("bZrYlw0clWwB6ZY8rBdgrbLL","vlinderugent:4MIJU6VliNUUW1VeVpJl9NHmvoxyvA2JK7mxJhQ");    // Vlinder 28 Gent
//ATT_NBIOT device("6VeMTnop5DCcops6rNVRDcBR","vlinderugent:4GPwrJOnzErXm0lqFyPmgl5wZ4LlI3GlVzzsCMC0");   // Vlinder 29 Gent
ATT_NBIOT device("4JX1mVgdkKnn8i3ueY9aaVXA","vlinderugent:4Mqq3uKWPyQze0Nw7zN8DrBlYAy5UzmVbcbWVRT3");   // Vlinder 30 Geraardsbergen
//ATT_NBIOT device("gL8ySh0fD0yikpZGaWQG61oH","vlinderugent:4HLzdGHYlQzfO0Nw7z08xqgT3Yy6oitO9uPPer90");   // Vlinder 31 Heist-op-den-Berg
//ATT_NBIOT device("36Ysu7TgQhOhkF2oJFiIoFLj","vlinderugent:4N52RQ3CIPzGG0lqFyfL0rc0yLHsJlg2blIOLlD1");   // Vlinder 32 Heist-op-den-Berg
//ATT_NBIOT device("ETJYb2VdWHhzRY0XIqW5Ldni","vlinderugent:4JI9RYa30eDAW1VeVoYEH7QhczudNBPhpONUQT7");    // Vlinder 33 Herentals
//ATT_NBIOT device("2MDSH0xR5dG2plS7R9ZLNutq","vlinderugent:4KZnRLaOALFhW1VeVsLg3Ies4FJzCK5G70hZrV6");    // Vlinder 34 Ieper
//ATT_NBIOT device("jtvKBelmZOkuCZMw2NpcaYxI","vlinderugent:4GbhR16za09SG0lqFykvZl5nWhc6IOOHGj9zYj90");   // Vlinder 35 Keerbergen
//ATT_NBIOT device("en06bHr9AwHDTwNnvhdtMFmy","vlinderugent:4KV85vE2qy96m0lqFyzLYit4RTtKaKAQEykP2AL0");   // Vlinder 36 Koekelberg
//ATT_NBIOT device("XcdmHK6Yw2NeVdAFM4djB59J","vlinderugent:4TDz8m09d8U7m0lqFv2Ci47fX6sKSICR7RRmyet");    // Vlinder 37 Kontich
//ATT_NBIOT device("wmOdkPszrgIG5CMd47zn3y08","vlinderugent:4Nz7ztCkCi9q80Nw7yqNxkpMS5wULtZezKfC5M40");   // Vlinder 38 Lier
//ATT_NBIOT device("eUPvvLdGP4DEbphRbM1wgjig","vlinderugent:4QNhtRR2hTpJW1VeVtIpjnj3GsJHMdc0Di2qkv0");    // Vlinder 39 Lommel
//ATT_NBIOT device("7DR6TiwO0x9hamaMswCc6578","vlinderugent:4OEXRLRcWmp0W1VeVmoRTfeNIaFDpxRc9p4TeQ1");    // Vlinder 40 Londerzeel
//ATT_NBIOT device("XeIIA97QzN5xxk6AvdzAPquY","vlinderugent:4NsTxZuyXjxMm0lqFx5JDzyce9dds5dMSjsoRie0");   // Vlinder 41 Maaseik
//ATT_NBIOT device("QNVdfKUcGfeaSoHnd1uLRn74","vlinderugent:4V2QzIYxEpr6m0lqFy2A3k8fiaBS7Rf1FbXQzdd1");   // Vlinder 42 Maldegem
//ATT_NBIOT device("N0EAjpEOhFCM9Q6hQdXommu8","vlinderugent:4JeHHSWgQvIvW1VeVmPENBK20ge8d1E78AUzJGO");    // Vlinder 43 Menen
//ATT_NBIOT device("V0sYUGN2UObPDcHRmrhUntEv","vlinderugent:4ULCYhMaQBkBW1VeVy19NEeIwyHNGzZw6I315ea1");   // Vlinder 44 Nieuwpoort
//ATT_NBIOT device("V1qJJx8s5dfvPgqyPmQ0Uvhq","vlinderugent:4UwOrUApdCzSm0lqFyk65323cMXCl2zys7COFnT2");   // Vlinder 45 Oudenaarde
//ATT_NBIOT device("J8SNioTAfAz5UNh0uIt9VE72","vlinderugent:4H4rAnpcG3bdW1VeVtDmvciwbzrNHfZXCyrP47O");    // Vlinder 46 Oudenaarde
//ATT_NBIOT device("hI1sYgmyyHsY74OKORcVjgIH","vlinderugent:4Pa1GQTHQJxoW1VeVzqE56wdlz7tXNXTondloEH");    // Vlinder 47 Pelt
//ATT_NBIOT device("yne5qgw98kSGqMNk2hHRHEgX","vlinderugent:4LHOZFzorpqYm0lqFyOXl0ykVImClcbWKOE5nCB1");   // Vlinder 48 Sint-Niklaas
//ATT_NBIOT device("V0Vrych4WeZJXlx9HnEzrtdB","vlinderugent:4L2JhNQ2PXluW1VeVwMVSwEtlyeW5qlsHfEWLE0");    // Vlinder 49 Sint-Niklaas
//ATT_NBIOT device("EpYBjkKLsYyRErDGstWeFI3A","vlinderugent:4RT4iLJZx7EsW1VeVqw52i5JHzwtfp04qZsYbG2");    // Vlinder 50 Sint-Truiden
//ATT_NBIOT device("DqtAUxOaYtpvQev7UdLAGni5","vlinderugent:4N2naJ9qpBRxW1VeVm5dsjXBYSQdBSfMYNzNynS");    // Vlinder 51 Sint-Truiden
//ATT_NBIOT device("CRjDzKhYB7Q0yrBMsvYrOABc","vlinderugent:4QbHdapzuNdAG0lqFvwzaihzPZEDe6DnTRjFTt60");   // Vlinder 52 Tielt
//ATT_NBIOT device("8NZZfd5wtnSZAJSABVLd4hA1","vlinderugent:4SfpdFGw6besW1VeVn0PlKBSXSmCNW9FUQGW0gD");    // Vlinder 53 Tielt
//ATT_NBIOT device("dIo3hFEg7DeF32Nj9fqUoDcp","vlinderugent:4VYHHmHt8LBzG0lqFzGkGzaAbyJlY4YdJMYuWV50");   // Vlinder 54 Tienen
//ATT_NBIOT device("IAKRIUlMMP39zdbXNEbCW3Re","vlinderugent:4T4Wzu8sl4FPG0lqFuChrOxqkfPznkrSzGtn1XO0");   // Vlinder 55 Veurne
//ATT_NBIOT device("zdaMx592RdPfr5bHa8h8bu4W","vlinderugent:4KdgED7YglHdW1VeVxwCUJQlIF4FbPjFwCuh0c3");    // Vlinder 56 Vorselaar
//ATT_NBIOT device("yig7e7HGi27NcwzIOgcvhBC2","vlinderugent:4SxA8WY2rjYcW1VeVrTPeiey1eKAI4LjIoi00E2");    // Vlinder 57 Zelzate
//ATT_NBIOT device("S1cUFJPTdRN13R1eTiXoH77C","vlinderugent:4OSn1rHdKzGgG0lqFuNiRQUtRg2C97TatzhDOVE");    // Vlinder 58 Zelzate
//ATT_NBIOT device("lOM9ntUwfV7154olxq9ylQcC","vlinderugent:4Pzl7Fxn4olFm0lqFu5kbMNJxIzzItX88GtMfPk0");   // Vlinder 59 Melle Proefhoeve 2
//ATT_NBIOT device("ULRkNeA9OIT41itKx9ArGEwP","vlinderugent:4QaWqKP3JdKtW1VeVmIknNI5eXoX1lJfh7O0ta2");    // Vlinder 60 Ieper Vesten
//ATT_NBIOT device("l7rFOO2GjgOciJAKIhm8mVZV","vlinderugent:4eFhoU440lltWQey32NQDJsQAIcwGdNam4yCqQxX");    // Vlinder 61 Maldegem
//ATT_NBIOT device("ALg8aViYNhDHRgwIW7ZB9l1y","vlinderugent:4IJ4xK9JsJwVGxUGtCkuYPr3IzcBeI7JyEmf43ge");    // Vlinder 62 Geraardsbergen
//ATT_NBIOT device("hnc0YxKu18Jw7OdqhA3g5Pyc","vlinderugent:4nYAVDe8pTipdoE2jIWOouGZ5kARPSgCu2qFywkO");    // Vlinder 63 Mechelen Nekkerspoel
//ATT_NBIOT device("8UMyHhYpXOQpejqup2upLBlV","vlinderugent:4zp8Ai7l5hDTUWQeQOyyr0yc5HVro0Uj04Lbedo4");    // Vlinder 64 Mechelen Dijle
//ATT_NBIOT device("WBOSyZXZgzSIK42bG8KfRkKW","vlinderugent:42LSdPEgVMk1ZIupV7HA3UeiP3Edw3bLrUS2SLRG");    // Vlinder 65 Herzele
//ATT_NBIOT device("qxCwQVK8J7frFmlSyNHY1vjS","vlinderugent:4QpmFNGonQlIw0alAxvmqTk7yDlAdOHYKGy0zQPh");    // Vlinder 66 Ninove
//ATT_NBIOT device("H3M4uDKhcoVHfnsBxcZv6BeL","vlinderugent:4dKjT5jdyoEte56ON5Iw0FNZbj2yFL1u87DDbHC2");    // Vlinder 67 Zottegem
//ATT_NBIOT device("w2iKDX5uZoe7gF0cUFAeMBo2","vlinderugent:4MdgLOT27vYzT146ATsZ4gyDnWN2BrYRZ5JYpM8P");    // Vlinder 68 Lier
//ATT_NBIOT device("g6fFNlSTajdUGUrsJDWEDgz4","vlinderugent:4cMvuoehEUEIwqiGC8ueKXZU0QiPYE3BvYkSUDPb");    // Vlinder 69 Lommel
//ATT_NBIOT device("tJ4tPJofKynz98YZ2f5dYLCR","vlinderugent:4JYuI9ZbJB2tki87760Z1NFL9H7pft6HKx3Mnk7Q");    // Vlinder 70 Poelkappelle
/*=============== G L O B A L    V A R I A B L E S ================*/
Adafruit_BME280 bme;           // define BME280 sensor with I2C comm.

#ifdef CBOR
  #include <CborBuilder.h>
  CborBuilder payload(device);
#endif
DateTime now;
unsigned char wxdata[8]={0};
int Temperature_i=0;
float Temperature_f=0.0;
float Humidity=0.0;
int Rain=0;
float WindDir=0.0;
int WindDirection[36];
float WindSpeed=0;
float SumTemp=0.0;
float SumHumid=0.0;
float SumWindSpeed = 0.0;
float MaxWindSpeed =0.0;
int ReadingsCounter=0;
int oldDate;
int currentDate;
bool FirstFlag = true;
float AverageTemp = 0.0;
float AverageHumid = 0.0;
float AverageWindSpeed = 0.0;
String DataString;
float BMEPres = 0.0;
bool FirstTime = true;
int Index=0;
int AverageWindDirection=0;
int MaxValue = 0;
float RainRate= 0;
float WindGust= 0;
bool setupModem(void);
int minute_old;

/*======================== S E T U P  =============================*/
void setup() {
  while (!setupModem()){
    ; //keep trying to connect modem
  }
  //LED1 Red, used for indicating netwerk status and errors in setup
  pinMode(LED1, OUTPUT);
  digitalWrite(LED1, HIGH);
  //turn on the Grove connectord
  pinMode(GROVEPWR, OUTPUT);
  digitalWrite(GROVEPWR, HIGH);

  //LED2 Green, used for indicating comm with Davis
  pinMode(LED2, OUTPUT);
  digitalWrite(LED2, LOW);

  //Initialise the Real Time Clock   
   Wire.begin();
   rtc.begin();    

  //Initialise the BME 280 sensor
  if (!bme.begin()) {
      DEBUG_STREAM.println("Error BME sensor");
      //Hang and blink RED led 2x / per second
      while (true){  
      digitalWrite(LED1, HIGH);
      delay(250);
      digitalWrite(LED1, LOW);
      delay(250);
      };
  }
  // force BME280 in weather monitoring mode : 1x sampling, filter off
  bme.setSampling(Adafruit_BME280::MODE_FORCED,
                  Adafruit_BME280::SAMPLING_X1, // temperature
                  Adafruit_BME280::SAMPLING_X1, // pressure
                  Adafruit_BME280::SAMPLING_X1, // humidity
                  Adafruit_BME280::FILTER_OFF   );
  
  //Turn off DEBUG stream and activate DAVIS stream
  DEBUG_STREAM.end();
  DAVIS_STREAM.begin(4800);
  ClearDAVIS_STREAM();
  for(int i=0; i<=35; i++){WindDirection[i]=0;}
} // End of Setp

/*========================= L O O P  ==============================*/

void loop() {

    if(DAVIS_STREAM.available()>=6)
    {
      wxdata[0] = DAVIS_STREAM.read();
      wxdata[1] = DAVIS_STREAM.read();
      wxdata[2] = DAVIS_STREAM.read();
      wxdata[3] = DAVIS_STREAM.read();
      wxdata[4] = DAVIS_STREAM.read();
      wxdata[5] = DAVIS_STREAM.read();

      WindDir = (wxdata[2] * 359.0 / 255.0);
      Index = round(WindDir/10)-1;
      WindDirection[Index] +=1;
      WindSpeed = wxdata[1] * 1.609; 
      
      switch(wxdata[0]>>4) //process packet based on sensor type
      {
        case 4: /* Add UV here */break;
        
        case 5: 
        if((wxdata[4] && 0x40)== 0x40) { //strong rain
          RainRate = 11520 / (((wxdata[4] && 0x30) / 16 * 250) + wxdata[3]);
        }
        else{ //light rain
          RainRate = 720 / (((wxdata[4] && 0x30) / 16 * 250) + wxdata[3]);
        }
        break;
        
        case 6: /* Add Solar here */break;
        
        case 8:
        Temperature_i=(wxdata[3]*0xff+wxdata[4]);
        Temperature_f=(Temperature_i/160.0);
        Temperature_f=(Temperature_f-32.0)/1.8; //celcius conversion
        break;
        
        case 9: 
        WindGust = wxdata[3] * 1.609;
        break;
        
        case 10:
        Humidity = (((wxdata[4]>>4)<<8)+wxdata[3])/10.0;
        break;
        
        case 14:
        Rain = (wxdata[3]); //0.2 L/m² per tip, but we send only the counter value, as integer
        break;
        
      }  //end of switch
      
      // add the values to the sum for averaging
      SumTemp += Temperature_f;        
      SumHumid += Humidity;
      SumWindSpeed += WindSpeed;
      if ( MaxWindSpeed < WindSpeed) 
        { MaxWindSpeed = WindSpeed;}

      ReadingsCounter +=1;    // add 1 to the ReadingsCounter
      ClearDAVIS_STREAM ();   // clear the serial port 
      
 
      // flash the green LED for visual check
      digitalWrite(LED2, HIGH);
      delay(DELAY_TIME);
      digitalWrite(LED2, LOW);
    
    }  //end of if available

// if now.minutes() ends with digit 0 or 5 ...  so every 5 minutes, but only 1x !!
    now = rtc.now(); //get the current date-time
    int checkvalue = now.minute() %5;
    if (checkvalue == 0 && minute_old!=now.minute()) { 
    minute_old = now.minute();
    
    // if first run of this 5 minute section

    if(FirstFlag == true){
      FirstFlag = false;
    }
    
    // calculate the averages for T, RH and Wind Speed. Calc difference between rain readings

        AverageTemp = SumTemp / ReadingsCounter;
        AverageHumid = SumHumid / ReadingsCounter;
        AverageWindSpeed = SumWindSpeed / ReadingsCounter;


    // find WindDirection which occured most
        MaxValue = WindDirection[0];
        Index=0;
        for(int i=0; i<=35; i++){
          if( WindDirection[i] > MaxValue){
            MaxValue = WindDirection[i];
            Index = i;
          }
        }
        AverageWindDirection = (Index *10)+5;

    // read the air presssure
        bme.takeForcedMeasurement(); // force BME280 to take measuremen
        BMEPres  = bme.readPressure();
    
    // communicate the data to AllThingsTalk
        DAVIS_STREAM.end();
        DEBUG_STREAM.begin(57600);
        if (device.isConnected()==false){
          int retryAttempts = 1;  
          while (!device.isConnected() && (retryAttempts < 3)){
            device.connect();
            delay(retryAttempts * 1000); //wait first time 1 second, then 2, then 3 seconds to reconnect
            retryAttempts++;
            //DEBUG_STREAM.println("loop1");
            //DEBUG_STREAM.println(retryAttempts);
          }  
        }
        if (device.isConnected()==false){ //check again to see if modem reset is required
          device.init(MODEM_STREAM, DEBUG_STREAM, MODEM_ON_OFF_PIN);
          int retryAttempts = 1;  
          while (!device.isConnected() && (retryAttempts < 3)){
            device.connect();
            delay(retryAttempts * 1000); //wait first time 1 second, then 2, then 3 seconds to reconnect
            retryAttempts++;
            //DEBUG_STREAM.println("loop2");
            //DEBUG_STREAM.println(retryAttempts);
          }  
        }
        payload.reset();
        payload.map(7);
        payload.addNumber(AverageTemp, "temperature");
        payload.addNumber((int)AverageHumid, "humidity");
        payload.addNumber((long)BMEPres, "pressure");
        payload.addNumber(AverageWindSpeed, "WindSpeed");
        payload.addNumber((int)AverageWindDirection, "WindDirection");
        payload.addNumber(Rain, "RainToDay"); 
        payload.addNumber(MaxWindSpeed, "WindGust");
        int retryAttempts = 1;
        while (!payload.send() && retryAttempts < 3) {
            device.init(MODEM_STREAM, DEBUG_STREAM, MODEM_ON_OFF_PIN);
            delay(retryAttempts * 1000);
            retryAttempts++;
        }
        if (retryAttempts<3){ 
          digitalWrite(LED1, HIGH);// set status led ON
        } 
        else{
          digitalWrite(LED1, LOW); // turn status led OFF
        }
        DEBUG_STREAM.end();
        DAVIS_STREAM.begin(4800);
        ClearDAVIS_STREAM();

    //  Reset the Sums, Counters etc
        SumTemp = 0.0;
        SumHumid = 0.0;
        SumWindSpeed = 0.0;    
        MaxWindSpeed = 0.0;
        ReadingsCounter = 0;
        for(int i=0; i<=35; i++){WindDirection[i]=0;}         
    }//end of if
    
// End of 5 minute task


} // End of Loop

/*================== S U B   R O U T I N E S ======================*/

// Clear the DAVIS_STREAM by reading until no more bytes available
void ClearDAVIS_STREAM(void){
    delay(200);
    if(DAVIS_STREAM.available())
    {
      do
      {
        DAVIS_STREAM.read();
        delay(20);
      }while(DAVIS_STREAM.available()); //clear bytes until empty so first packet is in sync
    }
}

bool setupModem(void)
{
  DEBUG_STREAM.begin(57600);
  MODEM_STREAM.begin(9600);
  device.init(MODEM_STREAM, DEBUG_STREAM, MODEM_ON_OFF_PIN);
  
  if(device.connect()){
      digitalWrite(LED2, HIGH);
    return true;
  }
  else
  {
      digitalWrite(LED2, LOW);
    return false;
  }
    
}
