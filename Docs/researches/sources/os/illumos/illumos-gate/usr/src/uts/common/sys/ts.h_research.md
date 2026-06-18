# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ts.h

## Purpose
Kernel header for the time-sharing scheduler class state and dispatch table entries.

## Main Interfaces
- Defines `tsdpent_t`, a dispatch table entry containing global priority, quantum, priority adjustment values, and maximum wait.
- Defines `tsproc_t`, per-thread time-sharing class state including CPU usage, user priority, nice-derived priority limits, interactive state, quantum, flags, thread pointer, and list links.
- Defines class flags such as `TSBACKQ`, `TSIA`, `TSIASET`, `TSIANICED`, and `TSRESTORE`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/thread.h`, and `sys/cpucaps.h`. Used by the TS scheduler class implementation and priority control interfaces.

## Research Notes
The scheduler state separates configured dispatch policy (`tsdpent_t`) from per-thread dynamic state (`tsproc_t`), including interactive heuristics.
