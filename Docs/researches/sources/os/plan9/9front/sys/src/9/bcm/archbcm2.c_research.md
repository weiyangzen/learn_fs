# File Research: sources/os/plan9/9front/sys/src/9/bcm/archbcm2.c

BCM2836/Raspberry Pi 2 and related multicore board support.

Key behavior:
- Defines `Soc` parameters for BCM2836-style I/O, ARM local registers, and SMP cache attributes.
- Implements watchdog reset/feed/disable and CPU identification for Cortex-A7/A53.
- Derives CPU count from hardware limit and optional `*ncpu`.
- Starts secondary CPUs using ARM local mailbox `startcpu` fields and `sev`.
- Provides mailbox clear/wake helpers.
- Coordinates secondary startup with per-CPU locks.
- `cpustart` performs per-secondary trap, clock, MMU, timer, FPU, active-mach, and scheduler setup.

Dependencies:
- Uses ARM local mailbox registers, `cpureset`, `machinit`, trap/clock/MMU/timer setup, and watchdog clock link.

Research notes:
- The SoC DRAM size is capped below physical I/O overlap.
