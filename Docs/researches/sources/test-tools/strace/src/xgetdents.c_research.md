<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xgetdents.c -->
# sources/test-tools/strace/src/xgetdents.c

Purpose: Shared decoder for `getdents`-style variable-length directory entry buffers, with callback hooks for entry head and tail layouts.

Important APIs/types/functions:
- Helper functions include `decode_dents`, `xgetdents`
- Direct includes: `"xgetdents.h"`, `"kernel_dirent.h"`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- iterates user-provided arrays with bounded element fetch callbacks

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- cover verbose versus abbreviated output modes
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xgetdents.c -->
