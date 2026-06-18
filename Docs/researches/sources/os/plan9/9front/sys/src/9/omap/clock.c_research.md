# File Research: sources/os/plan9/9front/sys/src/9/omap/clock.c

OMAP3530 timer, watchdog, delay, and fast-tick implementation.

Key behavior:
- Uses GPTIMER1 as a free-running 32 kHz base timer and GPTIMER2 as the interrupting kernel clock.
- `clockshutdown` resets timers and disables WDT2/WDT3.
- `clockinit` enables the ARM performance cycle counter, starts timer hardware, installs the clock interrupt, sanity-checks ticking, and calibrates delay loops.
- `clockintr` calls the generic `timerintr` and acknowledges timer overflow.
- `watchdoginit` enables periodic watchdog assurance through clock links.
- `timerset` programs the next timer interrupt within min/max bounds.
- `fastticks` returns a widened monotonically maintained value from the 32-bit cycle counter.
- `microdelay` and `delay` spin using `m->delayloop`.

Research notes:
- Comments explain OMAP timer clock source constraints and the choice to use 32 kHz GPTIMERs.
- Watchdog control uses the OMAP magic start/stop sequences.
