# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpsync.h

Purpose: Defines Ghostscript’s portable synchronization and thread-creation abstraction.

Key interfaces: opaque storage structs `gp_semaphore` and `gp_monitor`; size/open/close/wait/signal/enter/leave functions; `gp_thread_creation_callback_t`; and `gp_create_thread`.

Behavior: Size functions tell callers how much platform-specific storage to allocate. Passing `NULL` to open probes whether the object may be moved by the memory manager.

Dependencies: Implemented by platform files such as `gp_wsync.c`.

Risks and notes: The dummy structs are placeholders, so users must allocate storage based on runtime `sizeof` functions rather than C `sizeof(gp_semaphore)`.
