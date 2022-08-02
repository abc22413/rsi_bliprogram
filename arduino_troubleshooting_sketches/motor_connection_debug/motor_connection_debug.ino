const int pul = 52;
const int dir = 53;
const int a_prox = 51;
const int a_dist = 50;
const int b_prox = 45;
const int b_dist = 44;

const int c_pul = 35;
const int c_dir = 34;

int SPAN = 0;

void move_motor() {
  digitalWrite(pul, LOW);
  delay(2);
  digitalWrite(pul, HIGH);
  delay(2);
}

void calibrate() {
  digitalWrite(dir, HIGH);
  while(digitalRead(a_dist)!=1) {
    move_motor();
  }
  Serial.println("Distal!");
  SPAN = 0;
  digitalWrite(dir, LOW);
  while(digitalRead(a_prox)!=1) {
    move_motor();
    SPAN += 1;  
  }
  Serial.println("Prox!");
  SPAN -= SPAN%2;
  digitalWrite(dir, HIGH);
  for(int i=0;i<SPAN/2;i++) {
    move_motor();  
  }
  Serial.println("Calibrated");
}

void setup() {
  Serial.begin(115200);
  pinMode(pul, OUTPUT);
  pinMode(dir, OUTPUT);
  pinMode(c_pul, OUTPUT);
  pinMode(c_dir, OUTPUT);
  
  pinMode(a_prox, INPUT_PULLUP);
  pinMode(a_dist, INPUT_PULLUP);
  pinMode(b_prox, INPUT_PULLUP);
  pinMode(b_dist, INPUT_PULLUP);
}

void loop() {
  //wiring is done so A-red to black
  //dir=HIGH yields distal motion

  //calibrate();
  //delay(1000);

  digitalWrite(c_dir, HIGH);
  digitalWrite(c_pul, HIGH);
  delay(10);
  digitalWrite(c_pul, LOW);
  delay(10);
  
}
