# File Research: sources/os/plan9/9front/sys/src/9/sgi/clock.c

Provides SGI/MIPS clock initialization and timekeeping using the MIPS count/compare registers. `clockinit` estimates CPU speed with a calibrated instruction loop, sets delay-loop calibration, initializes `m->cyclefreq`, min/max timer periods, and enables interrupt level 7.

`clock` schedules the next compare interrupt and calls `timerintr`. `fastticks` accumulates monotonic ticks from `rdcount` under `splhi` to avoid recursive trap/interrupt reentry. `µs`, `microdelay`, `delay`, `perfticks`, and `timerset` provide the machine-dependent timing API.

The code assumes a 150 MHz Indy-style base and a count register that advances at half clock rate.
