# File Research: sources/os/bsd/openbsd-src/sys/sys/softintr.h

Machine-independent soft interrupt interface.

This small kernel-only header is enabled when `__USE_MI_SOFTINTR` is defined. It assigns soft interrupt levels for clock, network, and tty work, defines `NSOFTINTR`, and declares initialization, establish, disestablish, dispatch, and schedule functions.

Filesystem/storage relevance: indirect. Filesystem code generally runs in process or kernel thread context, but tty, network, and clock soft interrupts can wake descriptor waiters, update timers, or drive I/O-adjacent work.
