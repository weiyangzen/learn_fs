# File Research: sources/os/plan9/9front/sys/src/9/mtx/clock.c

This PowerPC MTX file implements the decrementer-based system clock and delay loops. `clockinit` hardcodes CPU and bus frequency, derives decrementer/timebase frequency, calibrates `m->loopconst`, computes `clkreload`, and programs DEC.

`clockintr` handles decrementer interrupts, compensates for late interrupts, updates ticks if needed, reloads DEC, and calls `timerintr`. `delay` and `microdelay` busy-wait using the calibrated loop constant. `fastticks`, `µs`, and `perfticks` expose low-overhead tick values.

Filesystem relevance is indirect: scheduler ticks, timers, sleeps, I/O timeouts, and cache/page daemon timing depend on this code.

Notable risks: CPU/bus frequencies are hardcoded; `timerset` is empty, so high-resolution timer support is absent.
