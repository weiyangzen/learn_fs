# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fault.h

## Role

`fault.h` defines process fault numbers used by `/proc` tracing. Faults are analogous to signals but correspond to hardware or low-level execution faults that debuggers can request to stop on.

## Definitions

Fault enumeration starts at 1 and includes illegal instruction, privileged instruction, breakpoint, trace trap, memory access/alignment, bounds, integer overflow, integer divide by zero, floating-point exception, stack fault, recoverable page fault, watchpoint trap, and CPU performance counter overflow.

`fltset_t` is a four-word bitset used to represent traced fault sets.
