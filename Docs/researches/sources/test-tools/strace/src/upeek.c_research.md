<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/upeek.c -->
# sources/test-tools/strace/src/upeek.c

Purpose: Low-level ptrace helper that reads a word from the tracee user area with `PTRACE_PEEKUSER` and reports non-ESRCH failures.

Important APIs/types/functions:
- Helper functions include `upeek`
- Direct includes: `"defs.h"`, `"ptrace.h"`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates with ptrace tracee access

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/upeek.c -->
