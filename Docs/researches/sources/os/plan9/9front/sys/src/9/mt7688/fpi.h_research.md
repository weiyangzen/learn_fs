# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fpi.h

Header for the MT7688 floating-point interpreter. It defines machine-independent FP word types, maps Plan 9 `FPdbleword` as `Double`, defines internal fraction/exponent constants, and declares the `Internal` representation.

`Internal` stores sign, exponent, low fraction with guard bits, and high fraction with hidden bit. Macros classify and set zero, infinity, and quiet NaN. The header declares arithmetic routines from `fpi.c` and conversion routines from `fpimem.c`.

Notable risks: comments state field order matters; conversion code depends on this representation and on Plan 9 double-word layout.
