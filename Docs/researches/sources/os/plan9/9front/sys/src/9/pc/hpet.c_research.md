# File Research: sources/os/plan9/9front/sys/src/9/pc/hpet.c

## Purpose
Implements HPET probing, CPU-frequency calibration, and monotonic fast-clock reads for the 9front PC kernel.

## Key Elements
`hpetprobe()` maps the HPET physical address, validates the period register, computes `hpet.freq` from femtoseconds-per-tick, and prints the discovered rate. `hpetinit()` starts HPET counting and uses `hpetcpufreq()` to calibrate `m->cpuhz`, `m->cpumhz`, `m->cyclefreq`, `m->delaylcycles`, and `m->loopconst`; secondary CPUs copy CPU timing values from CPU 0. `hpetread()` returns extended ticks by accumulating the 32-bit low counter into `hpet.last`.

## Dependencies
Uses kernel MMIO mapping (`vmap`), low-level cycle reading (`cycles`), delay calibration (`delayloop`), per-Mach CPU state, locks, and constants from `mem.h`/`io.h`.

## Behavior/Risks
The HPET is used for timing measurement, not interrupt generation; LAPIC/PIT paths provide interrupts elsewhere. Counter extension assumes calls occur often enough and under lock to interpret 32-bit wrap correctly. Invalid HPET periods return failure from probe.
