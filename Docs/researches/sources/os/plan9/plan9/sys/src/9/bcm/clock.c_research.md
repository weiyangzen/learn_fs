# File Research: sources/os/plan9/plan9/sys/src/9/bcm/clock.c

BCM2835 timer and delay implementation.

Key behavior:
- Uses system timer 3 at 1 MHz for clock interrupts and `fastticks()`.
- Uses ARM timer count register for `perfticks()` and immediate ARM timer interrupts.
- Measures CPU cycle frequency at boot by comparing `lcycles()` against system timer ticks.
- `clockintr()` acknowledges timer 3 and calls `timerintr()`.
- `timerset()` clamps next timer event between minimum and maximum periods.
- `fastticks()` reads the 64-bit system timer safely by retrying around high-word changes.
- `µs()`, `microdelay()`, and `delay()` provide timing primitives.
- `clockshutdown()` disables ARM timer and watchdog.

Dependencies include `IRQtimer3`, `IRQtimerArm`, `wdogoff()`, `timerintr()`, `lcycles()`, and global `m`.
