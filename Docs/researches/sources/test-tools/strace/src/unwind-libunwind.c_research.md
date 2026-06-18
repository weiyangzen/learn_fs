<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/unwind-libunwind.c -->
# sources/test-tools/strace/src/unwind-libunwind.c

Purpose: libunwind-ptrace backend that creates a remote address space, consults the mmap cache for executable mappings, resolves symbols, and walks tracee frames.

Important APIs/types/functions:
- Helper functions include `init`, `tcb_init`, `tcb_fin`, `get_symbol_name`, `print_stack_frame`, `walk`, `tcb_walk`
- Direct includes: `"defs.h"`, `"unwind.h"`, `"mmap_cache.h"`, `<libunwind-ptrace.h>`

Control flow:
- dispatches switch cases such as `MMAP_CACHE_REBUILD_RENEWED`, `MMAP_CACHE_REBUILD_READY`

State and persistence behavior:
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates with ptrace tracee access
- requires libunwind-ptrace support and mmap cache integration

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/unwind-libunwind.c -->
