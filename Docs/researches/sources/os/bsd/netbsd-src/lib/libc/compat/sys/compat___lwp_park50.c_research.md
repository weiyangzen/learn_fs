# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___lwp_park50.c

Read completely: 63 lines.

This implements `___lwp_park50`, adapting the old `__lwp_park` calling convention to `___lwp_park60`. It copies an optional relative-looking `timespec` pointer into a local and calls the newer API with `CLOCK_REALTIME` and `TIMER_ABSTIME`.

Important interactions: chained with `compat__lwp_park.c`, which converts `timespec50` to current `timespec` before reaching this layer.

Security/reliability notes: no heap allocation; timeout semantics are fixed by the chosen clock/flags.
