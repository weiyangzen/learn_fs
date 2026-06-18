# File Research: sources/os/plan9/plan9/sys/src/9/mtx/clock.c

## Role

Clock and delay implementation for the Plan 9 MTX PowerPC port. It configures the decrementer interrupt, tracks ticks, and supplies busy-wait delay and timestamp helpers.

This is platform timing infrastructure, not filesystem code.

## Main Interfaces

- `delayloopinit`
- `clockinit`
- `clockintr`
- `timerset`
- `delay`
- `microdelay`
- `fastticks`
- `µs`
- `perfticks`

## Important Behavior

- Computes `m->loopconst` from CPU frequency for busy-wait delay loops.
- Sets `m->dechz` to `m->bushz / 4`.
- Programs PowerPC decrementer through `putdec`.
- `clockintr` reloads the decrementer and calls `timerintr`.
- `fastticks` returns `m->ticks`; this is a low-resolution fallback.

## Dependencies And Assumptions

- Uses PowerPC decrementer accessors from assembly.
- Assumes `m->cpuhz` and `m->bushz` are initialized elsewhere.

## Notable Risks

- Busy-wait calibration is crude and CPU-frequency dependent.
- `fastticks` is tick-based, not true high-resolution cycle time.
