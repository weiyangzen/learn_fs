# sources/test-tools/strace/src/access.c

Purpose: syscall decoders for `access`, `faccessat`, and `faccessat2`.

Important APIs/types/functions: `decode_access`, `decode_faccessat`, `SYS_FUNC(access)`, `SYS_FUNC(faccessat)`, `SYS_FUNC(faccessat2)`, `printpath`, `print_dirfd`, `printflags`, and xlat tables `access_modes` and `faccessat_flags`.

Control flow: `access` decodes pathname and mode starting at argument 0. `faccessat` first prints `dirfd`, then reuses `decode_access` at offset 1. `faccessat2` extends `faccessat` decoding by printing argument 3 as flags.

State and persistence behavior: read-only decoder; no persistent state. It dereferences path arguments from the tracee using strace path-printing helpers.

Dependencies and integration points: included in `libstrace.a`; syscall table entries map access-family syscalls to these `SYS_FUNC`s. Xlat tables provide symbolic access and `AT_*` flag names.

Risks: `faccessat` and `faccessat2` differ only by flags; adding new access-like syscalls should preserve offset assumptions. Path decoding can fail if tracee memory is inaccessible.

Test signals: strace tests for `access`, `faccessat`, and `faccessat2` should show path, `R_OK/W_OK/X_OK/F_OK`, dirfd, and flags formatting.
