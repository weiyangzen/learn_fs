# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemlok.c

Implements `gs_memory_locked_t`, a monitor-locked wrapper around another `gs_memory_t`. Initialization installs a full procedure table and allocates a `gx_monitor_t`; release frees wrapper structures without freeing the target allocator.

Most methods enter the monitor, forward the allocation/free/status/root operation to the target, then leave the monitor. `free_all` frees only wrapper structures/allocator, not target data. `stable` lazily wraps the target’s stable allocator in another locked allocator when needed.

The wrapper serializes allocator access for multithreaded use while preserving the same memory-manager API.
