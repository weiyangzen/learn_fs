# File Research: sources/os/plan9/9front/sys/src/9/imx8/clock.c

Role: i.MX8 AArch64 generic timer, performance counter setup, delays, and CPU frequency measurement.

Key responsibilities:
- Enables PMU cycle counter and user access to virtual counter.
- Enables the physical timer and registers `IRQcntpns` as the clock interrupt.
- On CPU 0, reads `CNTFRQ_EL0`, prints timer frequency, and raises A53 root clock from 25 MHz to 1.6 GHz via CCM.
- Measures `m->cpuhz` from PMCCNTR over 1/100 second of generic counter time.
- Uses `CNTVCT_EL0` as user-visible cycle source frequency.
- Implements `timerset()`, `fastticks()`, `perfticks()`, `µs()`, `microdelay()`, and `delay()`.
- Synchronizes CPUs in `synccycles()` with two `Ref` barriers.

Dependencies:
- Uses ARM64 system registers, `setclkrate()`, and Plan 9 timer interrupt core.

Notes:
- `clockshutdown()` is empty.
- `timerset()` writes the raw signed interval to `CNTP_TVAL_EL0` without explicit lower/upper clamping.
