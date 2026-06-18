# File Research: sources/os/plan9/plan9/sys/src/9/port/edf.h

Purpose: Public EDF scheduler declarations and per-process EDF state structure.

Contents:
- Defines `Maxsteps`, EDF flag bits (`Admitted`, `Sporadic`, `Yieldonblock`, `Sendnotes`, `Deadline`, `Yield`, `Extratime`), and `Infinity`.
- Defines `struct Edf` with deadline/period/cost/slice fields, release/deadline timestamps, schedulability-test links, flags, embedded `Timer`, and accounting counters.
- Declares `edflock` and `edfunlock`.
- Registers format-check pragmas for EDF time formats.

Dependencies and integration:
- Requires `Proc` and `Timer` definitions from kernel headers.
