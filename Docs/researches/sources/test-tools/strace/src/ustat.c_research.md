<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ustat.c -->
# sources/test-tools/strace/src/ustat.c

Purpose: Decoder for legacy `ustat`, printing the device argument and, when headers are available, exit-side free block/inode counts from `struct ustat`.

Important APIs/types/functions:
- SYS_FUNC handlers: `ustat`
- Direct includes: `"defs.h"`, `DEF_MPERS_TYPE(struct_ustat)`, `<ustat.h>`, `MPERS_DEFS`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- participates in strace multi-personality builds for ABI-specific structures

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover native and compat personality builds where available
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ustat.c -->
