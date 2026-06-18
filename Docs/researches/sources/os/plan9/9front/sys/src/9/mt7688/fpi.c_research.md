# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fpi.c

Architecture-independent floating-point interpreter arithmetic core used by the MT7688 MIPS FP emulator path. It operates on the internal extended format defined in `fpi.h`.

It implements rounding, exponent matching, normalization/renormalization, add, subtract, multiply, divide, compare, and helper normalization. It handles zero, infinity, and NaN cases explicitly. The file notes that internal arguments to subtract/divide are reversed from naive expectation: `fpisub` computes `y - x`, and `fpidiv` computes `y / x`.

Multiplication uses chunked fixed-point partial products; division uses iterative subtract/shift quotient construction. Rounding uses guard bits and ties-to-even behavior.

Notable risks: arithmetic mutates `Internal` operands in places such as exponent matching and normalization, so callers need disposable copies where required.
