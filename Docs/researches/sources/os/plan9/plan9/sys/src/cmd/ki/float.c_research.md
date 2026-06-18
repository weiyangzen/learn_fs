# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/float.c

This file implements SPARC floating-point instruction behavior for `ki`.

It supports single and double floating loads/stores (`ldf`, `lddf`, `stf`, `stdf`), including immediate/register addressing, double alignment checks, and odd-register traps for double operations.

`fcmp()` implements SPARC floating compare variants, updates floating condition codes in `fpsr`, and handles NaN/invalid cases. `fbcc()` implements all floating branch conditions, annul behavior, taken counters, and delay-slot execution.

`farith()` implements floating add, subtract, multiply, divide, integer/float conversions, move, negate, absolute value, and single/double conversion operations. Division by zero raises a debugger-visible FP exception.

The implementation assumes host floating-point representation matches the constraints documented in `sparc.h`.
