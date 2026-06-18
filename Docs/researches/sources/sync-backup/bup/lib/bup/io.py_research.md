<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/io.py -->
# sources/sync-backup/bup/lib/bup/io.py

## Purpose
This module centralizes low-level process I/O, terminal-aware logging/progress display, shell/path quoting for messages, SQL quoting helpers, and a close-checked mmap subclass.

## Important APIs, Types, And Functions
Important functions are `log()`, `debug1()`, `debug2()`, `progress()`, `qprogress()`, `reprogress()`, `byte_stream()`, `enc_dsq()`, `enc_dsqs()`, `enc_sh()`, `enc_shs()`, `path_msg()`, `cmd_msg()`, `walk_path_msg()`, `qsql_id()`, and `qsql_str()`. `mmap` subclasses `mmap.mmap` to assert explicit closure.

## Control Flow
The module captures `initial_umask` at import without leaving it changed. `log()` flushes stdout, clears a prior progress line when needed, and writes to stderr through `_hard_write()`, which waits with `select()` and tolerates temporary `EAGAIN`. Progress functions only emit on tty-like stderr and throttle repeated updates.

## State And Persistence Behavior
State includes `initial_umask`, `buglvl` from `BUP_DEBUG`, tty flags from `BUP_FORCE_TTY`, and last progress-line tracking. It does not persist files itself, but its mmap wrapper enforces resource lifecycle for modules that map pack indexes and bup indexes.

## Dependencies And Integration Points
This module is imported by helpers, git, metadata, ls, protocol, main, and command modules for message formatting and logging. Its quoting functions are used in error messages, repair trailers, and command diagnostics.

## Risks And Edge Cases
`_hard_write()` assumes file-descriptor readiness semantics and could block indefinitely on broken descriptors. `enc_sh()` intentionally hex-escapes high-bit bytes for ASCII-compatible output, which is safe but not necessarily pretty. `walk_path_msg()` assumes VFS walk path layout with optional commit/tree prefixes. The mmap subclass asserts explicit closure in `__del__`, so leaked maps surface as assertion failures.

## Test Signals
`test/int/test_io.py`, `test/int/test_shquote.py`, CLI integration tests, and tests that intentionally leave or close mmaps validate quoting, progress/log behavior, byte/string path rendering, and close discipline.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/io.py -->
