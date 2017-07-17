
#include <Wire.h>
#include <SoftwareSerial.h>

String returnList = "";
int count = 0;



/*
   Message allocation
   0: ':'
   1: left button      + ','
   2: right button     + ','
   3: select button    + ','
   4: battery 1 volt   + ','
   5: battery 2 volt   + ','
   6: motor temp       + ','
   7: motorC temp      + ','
*/



int receiveData[6];

char leftButton;
char rightButton;
char selectButton;

String batOneVolt;
String batTwoVolt;
String motorTemp;
String motorCTemp;

float tempCalScale  = 1.0;
float tempCalOffset = 0.0;


void setup()
{
  Serial.begin(115200);
  Wire.begin(75);               // join i2c bus with address #75
  Wire.onRequest(requestEvent); // register request event
  Wire.onReceive(receiveEvent); // register receive event

  delay(100);

  Serial.println("setup complete"); //ONLY FOR TESTING

  pinMode(13, OUTPUT);
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
}

void loop()
{
  //battery 1 voltage
  batOneVolt = (String) ( ((float) analogRead(A0))*0.0147 );
  //battery 2 voltage
  batTwoVolt = (String) ( ((float) analogRead(A1))*0.0147 );

  //motorTemp
  motorTemp = (String) ( ((float) analogRead(A2))*tempCalScale + tempCalOffset);
  //motor controller temp
  motorCTemp = (String) ( ((float) analogRead(A3))*tempCalScale + tempCalOffset);

  leftButton = '0';
  rightButton = '0';
  selectButton = '0';

  //left button
  if(digitalRead(2) == HIGH)
    leftButton = '1';
    
  //right button
  if(digitalRead(3) == HIGH)
    rightButton = '1';
    
  //select button
  if(digitalRead(4) == HIGH)
    selectButton = '1';
  

}

String buildList() {
  int list_length = 10; // length with only seperators and button bytes
  int index = 0;


  list_length += (batOneVolt.length()+batTwoVolt.length()+motorTemp.length()+motorCTemp.length());

  char list[list_length];

  list[0] = ':';
  //Fix
  list[1] = leftButton;
  list[2] = ',';
  list[3] = rightButton;
  list[4] = ',';
  list[5] = selectButton;
  list[6] = ',';
  index = 6;
  //batOneVolt
  for(int i=1;i<batOneVolt.length();i++) {
    list[index+i] = batOneVolt.charAt(i);
    index++;
  }
  list[index+1] = ',';
  index++;
  //batTwoVolt
  for(int i=1;i<batTwoVolt.length();i++) {
    list[index+i] = batTwoVolt.charAt(i);
    index++;
  }
  list[index+1] = ',';
  index++;
  //motorTemp
  for(int i=1;i<motorTemp.length();i++) {
    list[index+i] = motorTemp.charAt(i);
    index++;
  }
  list[index+1] = ',';
  index++;
  //motorCTemp
  for(int i=1;i<motorCTemp.length();i++) {
    list[index+i] = motorCTemp.charAt(i);
    index++;
  }
  list[index+1]=',';
  return String(list);
}

void requestEvent() {
  digitalWrite(13, HIGH);
  if(count = returnList.length()) { //to initialize the list
    returnList = buildList();
  }
  if(count = returnList.length()-1) { //to fill the list after one complete send
    returnList = buildList();
  }

  Wire.write(returnList.charAt(count));
  count++;
  
  digitalWrite(13, LOW);
}

void receiveEvent(int howMany) {
  int count = 0;
  for (int i = 0; i < howMany; i++) {
    receiveData[i] = Wire.read();
  }
}

