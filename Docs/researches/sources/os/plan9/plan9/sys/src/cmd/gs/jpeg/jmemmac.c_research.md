# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemmac.c

Classic Mac OS system-dependent memory manager backend, requiring `USE_MAC_MEMMGR`. It uses fixed-address Macintosh Toolbox memory rather than C `malloc`.

Small and large JPEG allocations call `NewPtr` and are freed with `DisposePtr`. `jpeg_mem_available()` uses `CompactMem()` with a slop reserve and respects `max_memory_to_use`. Initialization returns `FreeMem()` as the default memory limit.

Backing store uses System 7 APIs. It checks Gestalt support for FSSpec and FindFolder, creates temp files in the Temporary Items folder, reads/writes with `SetFPos`, `FSRead`, and `FSWrite`, and deletes via `FSpDelete` on close.
