# File Research: sources/os/plan9/9front/sys/src/9/mt7688/clock.c

MT7688 MIPS clock implementation using CP0 count/compare. It calibrates CPU speed by timing an instruction loop against the count register, sets delay-loop calibration, initializes machine frequency fields, programs timer periods, and enables timer interrupt `INTR7`.

`fastticks` maintains a 64-bit-ish accumulated tick count across 32-bit count wrap and ensures compare is not too far in the future. `clock` dismisses timer interrupts by writing compare and calls `timerintr`. `timerset` clamps requested periods to min/max bounds.

Notable risks: `Basetickfreq` is hard-coded as `580 MHz / 2`; calibration assumes the loop instruction count and CP0 counter behavior match the SoC.
