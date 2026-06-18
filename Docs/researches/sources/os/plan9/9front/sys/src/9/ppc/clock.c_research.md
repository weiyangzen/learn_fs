# File Research: sources/os/plan9/9front/sys/src/9/ppc/clock.c

PowerPC decrementer clock setup and delay routines.

Key responsibilities:
- Calibrates `m->loopconst` against the decrementer in `delayloopinit()`.
- Initializes decrementer/timebase frequency assumptions and loads the decrementer for `HZ`.
- Handles decrementer interrupts by accounting elapsed ticks and reloading DEC.
- Implements busy-wait `delay()` and `microdelay()`.
- Provides `perfticks()` as a wrapper over `fastticks()`.

Dependencies:
- Uses PPC decrementer accessors from assembly and machine clock fields initialized by board code.
