# File Research: sources/os/plan9/9front/sys/src/9/port/edf.h

Defines EDF scheduler constants and the `Edf` structure. Flags cover admitted/sporadic tasks, yield behavior, notes, deadline state, and extra-time mode. Time fields are in microseconds and include deadline, inherited deadline, period, cost, remaining slice, release time, absolute deadline, next period start, and last scheduled time.

The struct embeds a `Timer`, schedulability-test fields, and accounting counters for EDF runtime, extra runtime, aging, periods, and missed deadlines. It declares `edflock` and `edfunlock`, plus format-check pragmas for EDF time formatting.
