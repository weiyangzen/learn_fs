<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xgetdents.h -->
# sources/test-tools/strace/src/xgetdents.h

Purpose: Header declaring getdents callback types and the shared `xgetdents` decoder entry point.

Important APIs/types/functions:
- Direct includes: `"defs.h"`
- Local/exported macros: `STRACE_XGETDENTS_H`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xgetdents.h -->
