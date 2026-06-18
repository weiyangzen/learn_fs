# File Research: sources/os/bsd/freebsd-src/sys/sys/_lock.h

Common lock object and debug macro definitions.

Key elements:
- Defines `struct lock_object` with name, flags, class data, and witness pointer.
- Under `_KERNEL`, derives `LOCK_DEBUG` from module/debug/profiling/tracing options.
- Defines file/line argument macros for debug and non-debug lock builds.

Dependencies:
- Forward-references `struct witness`.

Research notes:
- Shared base embedded by mutexes, rwlocks, sx locks, lockmgr locks, and rmlocks.
- Lock debug mode affects ABI/calling conventions for modules.
