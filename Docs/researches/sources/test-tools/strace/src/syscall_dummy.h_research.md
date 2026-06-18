# sources/test-tools/strace/src/syscall_dummy.h

Purpose: compile-time alias map for syscalls that are unfinished, unimplemented, deprecated, structurally equivalent to another decoder, or safely handled by `printargs`.

Important APIs/types/functions: many `#define sys_*` aliases map names to real decoders (`sys_acct` to `sys_chdir`, `sys_connect` to `sys_bind`, etc.) or to `printargs`; conditional definitions account for missing kernel structs and machine-specific support.

Control flow: preprocessor conditions select aliases based on architecture and available structs before syscall table inclusion.

State and persistence behavior: no runtime state; affects compiled dispatch table.

Dependencies and integration points: included by `syscall.h` and therefore by syscall table generation in `syscall.c`.

Risks: aliases encode semantic assumptions; if a syscall diverges from its alias, output becomes misleading. Architecture conditions must track kernel ABI support.

Test signals: generated syscall tables compile on all supported architectures, alias decoders print correct argument shapes, and unimplemented/deprecated calls fall back to raw argument output.
