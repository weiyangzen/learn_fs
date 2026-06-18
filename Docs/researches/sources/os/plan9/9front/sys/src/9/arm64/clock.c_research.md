# File Research: sources/os/plan9/9front/sys/src/9/arm64/clock.c

ARM64 virtual timer and timebase support.

Key behavior:
- Enables the performance counter and user-readable virtual counter access.
- Uses `CNTVCT_EL0` as `fastticks` and virtual timer interrupts as scheduler clock interrupts.
- Reads `CNTFRQ_EL0` on CPU 0 and stores it as `m->cyclefreq`.
- Programs `CNTV_TVAL_EL0` in `timerset`.
- Implements microsecond and millisecond busy waits.
- Provides `synccycles` rendezvous for multi-CPU startup synchronization.

Dependencies:
- Uses `sysrd/syswr`, timer interrupt registration, `timerintr`, and machine state.

Research notes:
- User-visible timing is based on the virtual counter rather than the PMU cycle counter.
