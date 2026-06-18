# File Research: sources/os/bsd/dragonflybsd/sys/sys/sleepqueue.h

This kernel header defines the sleep queue API used by sleep/wakeup, condition variables, pause, sx locks, and lockmgr-style waits.

Key responsibilities:
- Documents the sleep queue usage model:
  - lock a queue chain for a wait channel
  - add the current thread
  - optionally set timeout
  - wait or timed wait
  - signal/broadcast/abort/remove under queue lock
- Defines queue type and behavior flags:
  - `SLEEPQ_SLEEP`
  - `SLEEPQ_CONDVAR`
  - `SLEEPQ_PAUSE`
  - `SLEEPQ_SX`
  - `SLEEPQ_LK`
  - `SLEEPQ_INTERRUPTIBLE`
  - `SLEEPQ_UNFAIR`
  - `SLEEPQ_DROP`
- Declares DragonFly applicable APIs:
  - setup/teardown per thread
  - add, lock, release
  - signal, broadcast
  - timeout setup
  - sleep count
  - timed wait and signal-interruptible timed wait
  - type query
  - wait and signal-interruptible wait
- Keeps several FreeBSD-style APIs in `#if 0` as not applicable to DragonFly.

Important invariants:
- Sleep queue chain must be locked before signal/broadcast according to comments.
- Signal/broadcast return whether at least one swapped-out thread resumed; caller may need to kick proc0 after releasing the lock.
- Timeout macro converts ticks to `sbintime_t` using `tick_sbt` and `C_HARDCLOCK`.

Research notes:
- This header documents the contract around wait-channel queue locking even though many implementation details live elsewhere.
