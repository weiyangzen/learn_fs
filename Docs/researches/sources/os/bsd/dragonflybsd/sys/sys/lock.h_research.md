# File Research: sources/os/bsd/dragonflybsd/sys/sys/lock.h

Defines DragonFly’s general sleepable lock manager API. `struct lock` stores flags, timeout, shared/exclusive count bits, wait message, and exclusive holder. The header defines lock request types, count bit layout, external/control flags, return semantics, initializer macros, sysinit helpers, and inline dispatch through `lockmgr()`.

Filesystem relevance is central: mount locks, vnode locks, rename locks, and many VFS paths use lockmgr semantics for shared/exclusive locking, upgrades, downgrades, cancellation, retries, and reclaim-aware behavior.
