<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/chmod.c -->
## sources/test-tools/strace/src/chmod.c

Purpose: Decodes mode-changing syscalls: `chmod`, `fchmodat`, `fchmodat2`, and `fchmod`.

Important APIs and types: Shared `decode_chmod`, `decode_fchmodat`, and syscall decoders for the four syscalls.

Control flow: `decode_chmod` prints pathname and numeric mode at a caller-supplied argument offset. `chmod` uses offset 0. `fchmodat` prints `dirfd` then decodes path/mode at offset 1. `fchmodat2` adds `flags` using `fchmodat_flags`. `fchmod` prints fd and numeric mode.

State and persistence: No state.

Dependencies and integration: Uses `defs.h`, `<linux/fcntl.h>`, `xlat/fchmodat_flags.h`, `print_dirfd`, `printfd`, `printpath`, and `print_numeric_umode_t`.

Risks: `fchmodat2` flag xlat must track kernel additions. Mode is intentionally numeric, not symbolic.

Test signals: Tests should cover dirfd variants, `AT_EMPTY_PATH`, invalid flags, fd rendering, and mode formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/chmod.c -->
