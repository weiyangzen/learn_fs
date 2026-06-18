# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/hproc.c

Implements HTTP `/proc/...` introspection for the running Venti process using Plan 9 `libmach` and `libthread` internals.

It opens the current process text and memory, initializes symbol and register metadata, maps process memory, and reads thread/proc structures by address. It can print process lists, threads, thread stack summaries, full stack traces with parameters and locals, memory segments, file descriptors, and symbols.

`hproc()` dispatches `/proc/all`, `/proc/segment`, `/proc/fd`, `/proc/procs`, `/proc/threads`, `/proc/stacks`, and `/proc/symbols`, serializing access with a `QLock` because the global debug state is mutable. Output is plain text.

This file is highly Plan 9 specific and depends on private thread structure offsets from `/sys/src/libthread/threadimpl.h`.
