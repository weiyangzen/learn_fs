# File Research: sources/os/plan9/9front/sys/src/9/zynq/timer.c

Purpose: Zynq ARM timer and cycle-counter implementation.

Key behavior:
- `fastticks` reads the global timer high/low registers consistently and reports `timerhz`.
- `µs`, `microdelay`, and `delay` provide busy-wait timing.
- `timerset` programs the local timer for the next kernel timer deadline, clamping to 32-bit range.
- `timerirq` acknowledges local timer interrupt and calls `timerintr`.
- `timerinit` derives CPU/timer frequencies from SLCR PLL/clock registers, enables global/local timers, registers clock IRQ, and enables performance counters.
- `synccycles` synchronizes cycle counters across CPUs using two `Ref` barriers.

Integration notes: Uses `mpcore`, `slcr`, interrupt setup, performance-counter assembly helpers, and Plan 9 timer subsystem.

Risk/attention points: `synccycles` assumes all configured CPUs enter the barrier; incorrect `conf.nmach` or failed CPU startup would hang.
