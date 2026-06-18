# sources/test-tools/strace/src/linux/tile/syscallent1.h

## Purpose
Defines Tile secondary personality syscall entries for 32-bit/compat tracing.

## Important APIs, Types, and Functions
Defines `sys_ARCH_mmap sys_mmap_4koff` and `ARCH_WANT_SYNC_FILE_RANGE2 1` before including `../32/syscallent.h`. It appends the same Tile-specific `[244] cmpxchg_badaddr` and `[245] cacheflush` `printargs` entries.

## Control Flow and Integration
All behavior is compile-time table construction. The pre-include macros tune the generic 32-bit table for Tile ABI differences, then local rows fill the architecture-specific range.

## State and Persistence
No mutable state. Produces static metadata for personality 1.

## Dependencies
Depends on generic 32-bit syscall table macro hooks and Tile personality selection.

## Risks
Forgetting the macro overrides would decode Tile compat `mmap` or `sync_file_range2` incorrectly. The local arch-specific rows must remain aligned with the native table's Tile-specific range.

## Test Signals
Compat Tile traces should verify `mmap`, `sync_file_range2`, syscall 244, and syscall 245 decoding. Compile tests should ensure macro redefinitions do not leak beyond intended include context.
