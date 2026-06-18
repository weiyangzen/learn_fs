# File Research: sources/os/bsd/dragonflybsd/sys/sys/indefinite2.h

`indefinite2.h` implements inline indefinite-wait tracking. It includes `indefinite.h` and `globaldata.h`.

`indefinite_init()` initializes wait state and optionally reports the lock name/address in per-CPU counters. `indefinite_check()` pauses or yields in a loop, starts timing after `INDEF_INFO_START`, periodically computes elapsed time via TSC or ticks, updates collision counters, emits warnings by lock type, can print backtraces under `INVARIANTS`, and panics after prolonged spin-lock waits. `indefinite_done()` records final collision time and disables tracking.

This header is used by lock/spin/token loops to diagnose and account for long waits.
