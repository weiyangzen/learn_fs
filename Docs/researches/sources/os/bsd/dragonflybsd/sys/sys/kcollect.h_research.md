# File Research: sources/os/bsd/dragonflybsd/sys/sys/kcollect.h

Defines the fixed-format kernel statistics collection record `kcollect_t` and the 29-entry metric namespace. Metrics cover load, CPU percentages, swap, VM faults, memory states, syscall counts, path lookups, interrupts, IPIs, timers, and dynamic slots.

Kernel APIs allow registration/unregistration of callbacks and direct value/scale updates. Filesystem relevance is through `KCOLLECT_NLOOKUP`, which tracks path lookup activity, and VM/memory counters useful for filesystem workload diagnosis.
