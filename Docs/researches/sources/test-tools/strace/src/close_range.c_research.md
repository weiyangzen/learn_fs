<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/close_range.c -->
## sources/test-tools/strace/src/close_range.c

Purpose: Decodes the `close_range` syscall.

Important APIs and types: `SYS_FUNC(close_range)`.

Control flow: Prints `first`, `last`, and `flags`, using unsigned integer formatting for fd bounds and `close_range_flags` for the flags.

State and persistence: No state.

Dependencies and integration: Depends on `defs.h`, `<linux/close_range.h>`, and `xlat/close_range_flags.h`.

Risks: New flags require xlat updates. The decoder casts fd bounds to `unsigned int`, matching syscall semantics.

Test signals: Tests should cover zero flags, `CLOSE_RANGE_UNSHARE`, `CLOSE_RANGE_CLOEXEC`, max fd values, and unknown bits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/close_range.c -->
