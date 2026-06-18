# File Research: sources/os/plan9/9front/sys/src/9/bcm/clock.c

BCM283x timer support for system timer, ARM timer, cycle counter, and ARM generic timer.

Key behavior:
- Uses system timer 3 at 1 MHz for CPU 0 hzclock and `fastticks`.
- Uses local generic timer for secondary CPU clock interrupts when supported.
- Uses ARM timer for `perfticks` and immediate interrupt forcing.
- Calibrates CPU cycle frequency against the 1 MHz system timer.
- Programs next clock interrupt with min/max period bounds.
- Provides microsecond/millisecond delay functions.

Dependencies:
- Uses CP15 timer feature probing, interrupt registration, ARM local timer registers, and `timerintr`.

Research notes:
- CPU 0 must receive system timer interrupts; secondary CPUs must receive local generic timer interrupts.
