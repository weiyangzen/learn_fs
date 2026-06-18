# File Research: sources/teaching/os161/kern/include/spl.h

Defines the machine-independent interrupt priority interface used by low-level synchronization and interrupt-sensitive code. OS/161 reduces traditional BSD-style interrupt priorities to `IPL_NONE` and `IPL_HIGH`, with `spl0()` enabling interrupts, `splhigh()` disabling them, and `splx(old)` restoring a prior state.

The inline wrappers call `splx(IPL_NONE)` and `splx(IPL_HIGH)`. Lower-level `splraise(oldipl, newipl)` and `spllower(oldipl, newipl)` are used by `splx` and spinlock code to transition interrupt state explicitly.

Important invariant: SPL affects only the current processor. Correct nesting depends on callers saving the old return value and restoring it with `splx`.
