const int pul = 52;
const int dir = 53;
const int a_prox = 51;
const int a_dist = 50;
const int b_prox = 45;
const int b_dist = 44;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(pul, OUTPUT);
  pinMode(dir, OUTPUT);
  
  pinMode(a_prox, INPUT_PULLUP);
  pinMode(a_dist, INPUT_PULLUP);
  pinMode(b_prox, INPUT_PULLUP);
  pinMode(b_dist, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(digitalRead(b_prox));
}
