# File Research: sources/os/bsd/netbsd-src/sys/sys/syncobj.h

This kernel-facing header defines NetBSD scheduler synchronization-object operations. It is visible only for `_KERNEL` or `_KMEMUSER` after the public include guard.

Key interface details:
- Includes `<sys/wchan.h>` and forward-declares `struct lwp`.
- Defines `syncobj_t` as a const `struct syncobj`.
- `struct syncobj` contains:
  - fixed-size name storage,
  - flags,
  - boost priority,
  - callbacks for unsleep, priority change, priority lending, and owner lookup.
- Provides `syncobj_noowner(wchan_t)`.
- Defines sleep queue behavior flags: `SOBJ_SLEEPQ_SORTED`, `SOBJ_SLEEPQ_LIFO`, `SOBJ_SLEEPQ_NULL`.
- Declares built-in synchronization objects for callouts, condition variables, pause/park, mutexes, rw locks, scheduler, select, and generic sleep.

Research notes:
- This is a scheduler/synchronization abstraction boundary, not an implementation file.
- The owner callback and priority-lending callback make this relevant to priority inheritance and lock contention behavior.
- Consumers depend on the object layout and callback semantics to integrate sleeps with scheduler queues.
