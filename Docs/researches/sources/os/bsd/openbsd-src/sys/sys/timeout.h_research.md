# File Research: sources/os/bsd/openbsd-src/sys/sys/timeout.h

Declares the kernel timeout/callout structure. `struct timeout` stores circular queue linkage, absolute target time, callback, argument, optional KCOV process, tick time, flags, and kernel clock id.

Flags distinguish initialized, queued, triggered, process-context, and MPSAFE timeouts. Kernel API covers setup, relative add in ticks/sec/msec/usec/nsec, absolute `timespec` scheduling, deletion, deletion barriers, global barriers, clock adjustment, hardclock update, and startup. This is the timed deferred-callback primitive used by subsystems such as tty restart handling.
