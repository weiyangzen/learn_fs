# sources/storage-engines/sqlite/test/ossfuzz.c

## Purpose

`ossfuzz.c` adapts SQLite to Google OSS-Fuzz/libFuzzer. `LLVMFuzzerTestOneInput()` treats fuzz bytes as SQL, executes them against a memory-only SQLite database, and applies strict limits to avoid unbounded runtime, memory use, and output.

## Important APIs, Types, and Functions

Important elements are `LLVMFuzzerTestOneInput()`, `ossfuzz_set_debug_flags()`, debug flags `FUZZ_SQL_TRACE`, `FUZZ_SHOW_MAX_DELAY`, `FUZZ_SHOW_ERRORS`, the `FuzzCtx` struct, `progress_handler()`, `block_debug_pragmas()`, and `exec_handler()`.

## Control Flow

Inputs shorter than three bytes are ignored. If byte 1 is newline, byte 0 is a selector and SQL starts after it; otherwise selector defaults to `0xfd`. The harness opens `fuzz.db` with `SQLITE_OPEN_MEMORY`, installs a frequent progress handler with a ten-second cutoff, limits VDBE ops, LIKE/GLOB pattern length, heap, and value length, configures foreign keys from selector bit 0, denies debug pragmas, derives output-row budget from remaining selector bits, copies input into a nul-terminated SQL string, calls `sqlite3_complete()` when available, runs `sqlite3_exec()`, cleans temp-directory state, and closes.

## State and Persistence Behavior

The DB is memory-only. Global state includes debug flags and SQLite’s hard heap limit. The harness explicitly resets `PRAGMA temp_store_directory=''` before closing to avoid fuzz SQL leaving global process state behind.

## Dependencies and Integration Points

It uses the libFuzzer `LLVMFuzzerTestOneInput` ABI and SQLite public APIs. `ossshell.c` links against it for local replay. It conditionally depends on progress callback and complete APIs depending on build options.

## Risks and Test Signals

The hard heap limit is global to SQLite. The selector protocol means leading bytes alter harness behavior. `FUZZ_SQL_TRACE` is exposed but not visibly implemented. Wall-clock progress timing can vary. OSS-Fuzz signals are crashes, sanitizer findings, leaks, assertions, and timeouts; local signals include optional errors and progress statistics.
