<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/unwind-libdw.c -->
# sources/test-tools/strace/src/unwind-libdw.c

Purpose: elfutils libdwfl unwinder backend that attaches DWARF state to tracees, refreshes mapping reports on mmap generation changes, caches frame metadata, and emits symbol/source frames.

Important APIs/types/functions:
- Helper functions include `update_mapping_generation`, `init`, `tcb_init`, `tcb_fin`, `flush_cache_maybe`, `frame_callback`, `tcb_walk`
- Direct includes: `"defs.h"`, `"unwind.h"`, `"mmap_notify.h"`, `"static_assert.h"`, `<elfutils/libdwfl.h>`
- Local/exported macros: `STRACE_UW_CACHE_SIZE`, `STRACE_UW_CACHE_ASSOC`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written
- tracks mmap generation changes to invalidate stale unwind symbol mappings

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- requires elfutils libdwfl support at build/run time

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- kernel/userspace structure layout drift is guarded by build-time assertions but still needs architecture coverage

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/unwind-libdw.c -->
