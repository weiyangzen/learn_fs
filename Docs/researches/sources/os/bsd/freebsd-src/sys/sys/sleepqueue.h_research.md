# File Research: sources/os/bsd/freebsd-src/sys/sys/sleepqueue.h

Kernel sleep queue interface for blocked threads.

Key responsibilities:
- Documents the sleep queue protocol used by sleep/wakeup, condition variables, pause, sx locks, and lockmgr.
- Defines sleep queue type and behavior flags: `SLEEPQ_SLEEP`, `SLEEPQ_CONDVAR`, `SLEEPQ_PAUSE`, `SLEEPQ_SX`, `SLEEPQ_LK`, `SLEEPQ_INTERRUPTIBLE`, `SLEEPQ_UNFAIR`, and `SLEEPQ_DROP`.
- Declares allocation, free, lock, add, release, remove, abort, signal, broadcast, timeout, timed wait, wait, type, count, and matching-removal routines.
- Provides `sleepq_set_timeout()` wrapper using hardclock ticks.

Important patterns:
- Sleep queues are keyed by wait channel.
- Threads allocate sleep queue objects at thread creation, but queues are not permanently owned by one thread.
- Wakeups require the sleep queue chain lock for non-racy signal/broadcast/remove operations.
- Interruptible and timed wait variants are separate entry points.

Research relevance:
- Fundamental scheduler blocking API beneath many filesystem, VM, socket, and driver wait paths.
