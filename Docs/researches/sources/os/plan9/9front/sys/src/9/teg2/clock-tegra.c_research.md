# File Research: sources/os/plan9/9front/sys/src/9/teg2/clock-tegra.c

Handles Tegra 2 SoC timers outside the Cortex private timers. It models four shared 29-bit countdown timers and the 32-bit 1 MHz microsecond counter.

`tegclock0init` arms the shared Tegra watchdog timer and registers `tegwdogintr`; `tegclockshutdown` disables it on CPU0. `tegclockinit` verifies the freerunning microsecond counter configuration and movement. `perfticks` returns the microsecond counter, keeping zero from being returned.

The shared watchdog requires clearing interrupt state and reading trigger to satisfy hardware/documentation quirks.
