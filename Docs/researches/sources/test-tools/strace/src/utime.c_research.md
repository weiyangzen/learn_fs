<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/utime.c -->
# sources/test-tools/strace/src/utime.c

Purpose: Decoder for `utime`, printing pathname and `struct utimbuf` access/modification times with human-readable comments.

Important APIs/types/functions:
- SYS_FUNC handlers: `utime`
- Direct includes: `"defs.h"`, `DEF_MPERS_TYPE(utimbuf_t)`, `<utime.h>`, `MPERS_DEFS`

Control flow:
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- participates in strace multi-personality builds for ABI-specific structures

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover native and compat personality builds where available
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/utime.c -->
