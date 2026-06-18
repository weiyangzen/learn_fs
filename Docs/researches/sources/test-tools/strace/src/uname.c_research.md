<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/uname.c -->
# sources/test-tools/strace/src/uname.c

Purpose: Exit-side decoder for `uname`, fetching `struct utsname` and printing system, node, release, version, machine, and optional domain fields with abbreviated-mode support.

Important APIs/types/functions:
- SYS_FUNC handlers: `uname`
- Direct includes: `"defs.h"`, `<sys/utsname.h>`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover verbose versus abbreviated output modes
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/uname.c -->
