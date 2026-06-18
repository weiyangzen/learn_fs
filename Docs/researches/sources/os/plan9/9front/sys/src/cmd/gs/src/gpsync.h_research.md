# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpsync.h

Purpose: Platform-independent interface for synchronization and thread creation.

Types and API: Defines opaque placeholder structs for `gp_semaphore` and `gp_monitor`, size queries, open/close/wait/signal or enter/leave operations, and `gp_create_thread`.

Important convention: Calling `gp_semaphore_open(NULL)` or `gp_monitor_open(NULL)` reports whether the memory manager may move the object after creation. This supports GC-aware placement of platform synchronization objects.

Dependencies and notes: Thread callbacks have type `void (*)(void *)`; platform implementations must bridge this to native thread entry APIs.
