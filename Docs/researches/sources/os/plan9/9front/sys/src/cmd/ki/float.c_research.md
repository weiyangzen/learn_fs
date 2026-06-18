# File Research: sources/os/plan9/9front/sys/src/cmd/ki/float.c

Floating-point instruction emulation for `ki`. It implements single/double FP loads and stores, alignment checks, FP comparisons with ordered/unordered condition encoding in `fpsr`, floating branches with annul and delay-slot behavior, and arithmetic/conversion operations for add, sub, mul, div, integer/float conversion, move, negate, abs, and single/double conversion.

The code updates simulated FP register unions directly and uses `longjmp(errjmp, 0)` for exceptions such as alignment faults, invalid FP registers, and divide-by-zero. It cooperates with `run.c` dispatch tables through `fcmp`, `fbcc`, and `farith`.
