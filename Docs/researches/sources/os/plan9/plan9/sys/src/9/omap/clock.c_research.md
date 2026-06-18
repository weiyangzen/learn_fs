# File Research: sources/os/plan9/plan9/sys/src/9/omap/clock.c

Implements OMAP3530 timer, fast tick, delay, and watchdog support.

Key points:
- Uses 32.768kHz timer clocks; GPTIMER1 is the free-running base timer and GPTIMER2 is the periodic interrupt timer.
- Defines OMAP timer/watchdog register layout and reset/start/interrupt bits.
- `clockshutdown()` resets/disables watchdog timers and both used general-purpose timers.
- Watchdog helpers perform OMAP magic start/stop sequences and register a periodic assurance callback.
- `clockintr()` handles timer interrupts, avoids nested timer processing, calls `timerintr()`, and acknowledges overflow.
- `clockinit()` shuts down timers, enables CP15 cycle counter access, initializes `m->fastclock`, starts free-running timer, enables interrupting timer on IRQ 38, verifies interrupts arrive, estimates MIPS loops, sets `delayloop`, and desynchronizes CPUs.
- `timerset()` programs the next timer interrupt within min/max bounds derived from HZ.
- `fastticks()` maintains a 64-bit fast clock from the 32-bit CP15 cycle counter, handling wraparound under a lock.
- `perfticks()`, `lcycles()`, `µs()`, `microdelay()`, and `delay()` expose timing primitives.

Dependencies and interactions:
- Assumes clock-source selections and timer clocks were enabled in `archomap.c`.
- Uses CP15 helpers from `coproc.c`.
- Calls Plan 9 timer, watchdog, and clock-link infrastructure.
- `devcons.c` reads time through `cycles()`/`fastticks()` paths.

Research relevance:
- OMAP platform’s timebase, scheduler tick, watchdog, and delay implementation.
