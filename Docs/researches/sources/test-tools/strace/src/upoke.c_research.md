<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/upoke.c -->
# sources/test-tools/strace/src/upoke.c

Purpose: Low-level ptrace helper that writes a word to the tracee user area through `ptrace_pokeuser` and reports non-ESRCH failures.

Important APIs/types/functions:
- Helper functions include `upoke`
- Direct includes: `"defs.h"`, `"ptrace.h"`, `"ptrace_pokeuser.c"`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/upoke.c -->
