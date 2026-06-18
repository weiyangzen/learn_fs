# File Research: sources/os/bsd/freebsd-src/sys/sys/timeet.h

Kernel event timer interface between hardware timer drivers and machine-independent timer code.

Key responsibilities:
- Defines `struct eventtimer` with list linkage, name, capability flags, quality, active state, frequency, minimum/maximum periods, start/stop callbacks, event/deregister callbacks, private argument fields, and sysctl node.
- Defines event timer capabilities for periodic, one-shot, per-CPU, C3-stop, and power-of-two divisor behavior.
- Declares global event timer mutex and `ET_LOCK`/`ET_UNLOCK` wrappers.
- Declares driver registration/deregistration/frequency-change APIs and consumer APIs for finding, initializing, starting, stopping, banning, and freeing event timers.
- Exposes the `_kern_eventtimer` sysctl tree when `SYSCTL_DECL` is available.

Dependencies:
- Kernel-only; includes lock, mutex, queue, and time headers.

Notable risks:
- Header guard names reference `TIMEEC`/`TIMETC` inconsistently, but the guard still protects this file.
- Correct capability flags and quality ordering are critical to timer selection and suspend/CPU-idle behavior.
