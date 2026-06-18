# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jmemmac.c

Purpose: Classic Mac OS system-dependent memory-manager backend.

Important behavior:
- Requires `USE_MAC_MEMMGR`.
- Uses Macintosh Toolbox memory APIs rather than C `malloc`.
- Small and large JPEG allocations call `NewPtr`.
- Frees memory with `DisposePtr`.
- `jpeg_mem_available()` uses `CompactMem()` with a slop reserve and respects `max_memory_to_use`.
- Initialization returns `FreeMem()` as the default memory limit.

Backing store:
- Uses System 7 APIs.
- Checks Gestalt support for `FSSpec` and `FindFolder`.
- Creates temporary files in the Temporary Items folder.
- Reads/writes with `SetFPos`, `FSRead`, and `FSWrite`.
- Deletes backing files with `FSpDelete` on close.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jmemsys.h`, Mac OS headers/APIs.
