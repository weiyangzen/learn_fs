# File Research: sources/os/plan9/plan9/sys/src/9/ppc/clock.c

## Role

Implements PPC clock/decrementer initialization and busy-wait delays.

## Control Flow

`clockinit` sets decrementer frequency to `m->bushz/4`, assumes time-base frequency equals decrementer frequency, calibrates delay loops, computes `clkreload`, and loads the decrementer. `clockintr` accounts elapsed decrementer ticks and reloads the decrementer, handling late interrupts by incrementing `m->ticks` by multiple reload intervals.

`delayloopinit` calibrates `m->loopconst` by measuring a 1 ms delay against the decrementer. `delay` and `microdelay` spin for approximate time using `loopconst`. `perfticks` returns `fastticks`.

## Dependencies

Uses PPC decrementer accessors `getdec`/`putdec`, `fastticks`, `HZ`, and `Mach` frequency fields.

## Risks

Timing accuracy depends on `m->bushz`, the 604e decrementer assumption, and initial loop calibration. Busy waits are CPU-local and not power efficient.
