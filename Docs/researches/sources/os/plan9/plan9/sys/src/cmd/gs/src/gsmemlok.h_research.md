# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemlok.h

Declares `gs_memory_locked_t`, which embeds `gs_memory_common` and stores a target allocator plus `gx_monitor_t`. The header documents that this wrapper does not track acquired memory itself, so `free_all` with `FREE_ALL_DATA` is effectively a no-op at the wrapper level.

Exports init, release, and target-accessor functions.
