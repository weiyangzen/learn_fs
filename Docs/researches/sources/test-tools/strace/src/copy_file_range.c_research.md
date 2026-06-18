<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/copy_file_range.c -->
## sources/test-tools/strace/src/copy_file_range.c

Purpose: Decodes `copy_file_range`.

Important APIs and types: `SYS_FUNC(copy_file_range)`.

Control flow: Prints input fd, input offset pointer as signed 64-bit value via `printnum_int64`, output fd, output offset pointer, length, and raw unsigned flags.

State and persistence: No state.

Dependencies and integration: Depends on `defs.h`, `printfd`, and integer pointer-print helpers.

Risks: Flags are raw numeric because no symbolic xlat is used. Offset pointers are decoded as values at addresses, so unreadable pointers fall back through `printnum_int64` behavior.

Test signals: Tests should cover null offsets, readable offsets, fd paths, large lengths, non-zero flags, and error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/copy_file_range.c -->
