# File Research: sources/teaching/os161/kern/include/clock.h

Declares kernel timekeeping and clock tick interfaces.

Key contents:
- `HZ` is 100 hardclock ticks per second.
- Declares hardclock bootstrap/tick, once-per-second `timerclock`, `gettime`, `timespec_add`, `timespec_sub`, and `clocksleep`.

Relevance:
- Supports timestamp and sleep-related kernel facilities; the listed SFS/semfs code does not set timestamps but `stat` ABI contains time fields.
