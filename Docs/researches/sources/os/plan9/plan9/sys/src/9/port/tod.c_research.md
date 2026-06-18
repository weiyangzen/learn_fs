# File Research: sources/os/plan9/plan9/sys/src/9/port/tod.c

## Role

Implements kernel time-of-day conversion around the fastest available tick counter. It converts fast ticks to nanoseconds, microseconds, and back using fixed-point multipliers.

## Main State

A single locked `tod` structure tracks initialization, frequency, fixed-point conversion multipliers/dividers, last tick reading, epoch offset, monotonic last return, and gradual correction state. It assumes multiprocessor fast clocks are synchronized.

## Control Flow

`todinit` samples `fastticks`, sets frequency, and registers `todfix` as a periodic clock callback. `todsetfreq` recomputes conversion factors with `mk64fract`. `todset` either sets absolute time or applies a gradual `delta` over `n * HZ` ticks. `todget` locks around `fastticks`, applies pending correction, converts elapsed ticks to epoch nanoseconds, and clamps time so it never moves backward.

`todfix` periodically folds elapsed ticks into `tod.off` to reduce overflow risk. Public helpers expose seconds, fastticks-to-us/ns, and us/ms/ns-to-fastticks conversions.

## Dependencies

Uses kernel locks, `fastticks`, `MACHP(0)->ticks`, `addclock0link`, `mul64fract`, `HZ`, and Plan 9 fixed-width integer types.

## Risks

The design relies on synchronized CPU tick counters. `todfix` contains a debug `iprint` for large conversions. `mk64fract` uses `(to<<32)/from`, so callers must avoid invalid or overflowing ratios; `todsetfreq` panics on nonpositive frequency.
