# File Research: sources/os/plan9/9front/sys/src/9/ppc/saturntimer.c

Saturn/UCU timer implementation.

Key responsibilities:
- Defines Saturn timer registers and event/enable bits.
- Initializes timer0 for scheduler interrupts and timer1 as a free-running one-second counter source.
- Handles timer interrupts, acknowledges timer0/timer1 events, increments high-level tick counter, acknowledges board interrupt state, and calls generic `timerintr()`.
- Implements `fastticks()` using timer1 plus an overflow counter.
- Implements `timerset()` by programming timer0 to a bounded future offset while preserving timer1.

Dependencies:
- Uses `msaturn.h` vectors, board interrupt acknowledgement, generic timer subsystem, and bus frequency from `m`.
