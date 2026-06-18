# File Research: sources/os/bsd/dragonflybsd/sys/sys/microtime_pcpu.h

Defines a per-CPU monotonic microtime helper. `union microtime_pcpu` stores either a `timeval` or TSC value. `microtime_pcpu_get()` uses invariant TSC when available, otherwise `microuptime`; `microtime_pcpu_diff()` returns elapsed microseconds.

Useful for low-overhead timing in kernel subsystems, with the caveat that monotonicity is only guaranteed on the same CPU.
