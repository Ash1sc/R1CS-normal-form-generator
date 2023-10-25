pragma circom 2.1.2;


template Multiplier() {
signal input a;
signal input c;
 signal output b;
 signal output e;

 var x = a*a;
 x += 3;
 e <== x;
 x += c;
 b <== x;

}

component main = Multiplier();