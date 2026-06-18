<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/uid16.c -->
# sources/test-tools/strace/src/uid16.c

Purpose: 16-bit UID/GID compatibility decoder wrapper; it defines `STRACE_UID_SIZE 16` and includes `uid.c` so legacy uid16 syscall variants reuse the generic UID decoder with 16-bit element widths.

Important APIs/types/functions:
- Direct includes: `"uid.c"`
- Local/exported macros: `STRACE_UID_SIZE`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/uid16.c -->
