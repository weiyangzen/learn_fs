<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/umask.c -->
# sources/test-tools/strace/src/umask.c

Purpose: Decoder for `umask`, printing the new file-mode creation mask in numeric/octal mode and tagging the syscall return as octal.

Important APIs/types/functions:
- SYS_FUNC handlers: `umask`
- Direct includes: `"defs.h"`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/umask.c -->
