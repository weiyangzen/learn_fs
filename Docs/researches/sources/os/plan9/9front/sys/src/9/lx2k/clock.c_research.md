# File Research: sources/os/plan9/9front/sys/src/9/lx2k/clock.c

LX2K ARM64 clock and delay implementation using the ARM generic timer and performance counter. It enables PMCCNTR, user access to counters, CNTP timer operation, computes CPU frequency by measuring PM cycles over a generic-timer interval, and registers the physical non-secure timer interrupt.

`fastticks` reads `CNTPCT_EL0` and reports `CNTFRQ_EL0`; `timerset` programs `CNTP_TVAL_EL0`; `microdelay` and `delay` spin on computed microseconds. `synccycles` provides a barrier-style multi-CPU synchronization helper, though this platform header sets `MAXMACH` to one.

Notable risks: `clockshutdown` is empty; CPU frequency measurement assumes a stable counter and PMCCNTR setup.
