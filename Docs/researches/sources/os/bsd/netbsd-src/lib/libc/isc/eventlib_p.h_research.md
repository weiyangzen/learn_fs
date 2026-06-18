# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/eventlib_p.h

Read completely: 283 lines.

This is eventlib's private header. It defines common error/allocation macros, debug memory fill behavior, private structures for connections, accepts, files, streams, timers, waits, and queued event records, plus the central `evContext_p` implementation structure.

The context aggregates current event state, debug output, connection/file lists, fd sets or poll arrays, stream queues, timer heap, last event time, and wait lists. When `USE_POLL` is enabled, it replaces fd-set macros with poll-backed emulation helpers.

Important interactions: `ev_timers.c`, stream/wait/file code, and event loop internals share these struct layouts. It remaps internal symbols such as `evPrintf`, `evCreateTimers`, `evDestroyTimers`, and `evFreeWait` onto `__ev*` names.

Security/reliability notes: this header exposes broad internal mutable state and raw linked-list/heap ownership. The `OKNEW`/`FREE` macros assume memcluster allocation sizes match exact object types. Poll/fd-set abstraction changes the semantics of `FD_*` macros in files that include this header.
