<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/wait.h -->
# sources/test-tools/strace/src/wait.h

Purpose: Wait-status compatibility header defining/fixing `WCOREFLAG`, `WCOREDUMP`, `W_STOPCODE`, `W_EXITCODE`, and `W_CONTINUED` for portable wait status decoding.

Important APIs/types/functions:
- Direct includes: `"defs.h"`, `<sys/wait.h>`, `"static_assert.h"`
- Local/exported macros: `STRACE_WAIT_H`, `WCOREFLAG`, `WCOREDUMP`, `W_STOPCODE`, `W_EXITCODE`, `W_CONTINUED`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- kernel/userspace structure layout drift is guarded by build-time assertions but still needs architecture coverage

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/wait.h -->
