# File Research: sources/os/plan9/9front/sys/src/9/teg2/clock.c

Cortex-A private timer and Plan 9 clock implementation for Tegra 2. It uses the Tegra 1 MHz counter as `fastticks` and Cortex local timers for periodic scheduling interrupts. It also contains optional local-watchdog code and multi-CPU clock sanity checks.

`clockinit` shuts down old timers, enables ARM cycle counters, validates the microsecond counter and local timer, installs the local timer IRQ, calibrates delay loops on CPU0, starts watchdogs, desynchronizes per-CPU timers, and arms periodic ticks. `clockintr` clears local timer interrupt state, calls `timerintr`, appeases the Tegra watchdog, and checks secondary CPU clock progress.

`fastticks` extends the 32-bit microsecond counter to a per-Mach 64-bit value under `splhi`. `timerset` converts fasttick targets to local-timer cycles with min/max clamping.
