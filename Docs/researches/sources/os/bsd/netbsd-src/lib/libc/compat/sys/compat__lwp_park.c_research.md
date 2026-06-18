# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat__lwp_park.c

Read completely: 66 lines.

This implements old `_lwp_park` taking `timespec50`. It converts an optional timeout to current `timespec` and calls `___lwp_park50`.

Security/reliability notes: direct stack-only conversion wrapper. Timeout pointer may be null and is handled.
