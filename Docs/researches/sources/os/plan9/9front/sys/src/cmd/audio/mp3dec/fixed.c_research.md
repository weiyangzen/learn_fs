# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/fixed.c

This file provides C helper routines for libmad fixed-point arithmetic. `mad_f_abs` returns the absolute value of a fixed-point integer. `mad_f_div` performs fixed-point division using integer quotient/remainder expansion, rounding, sign correction, and overflow guarding against the fixed-point representable range.

The decoder uses a 28-fraction-bit fixed-point format defined in `fixed.h`, so division must produce values scaled into the same representation. `mad_f_div` first computes an integer quotient, then iteratively shifts remainder bits into the fractional field until either all fraction bits are generated or the remainder reaches zero. It rounds based on the final remainder.

Most multiplication is macro/assembly driven in `fixed.h`; this file contains the few arithmetic routines that are easier or more portable as functions. Correctness here affects requantization, synthesis math, and Layer I/II scaling wherever division or absolute value is required.
