# sources/storage-engines/sqlite/src/test_malloc.c

## Purpose

`test_malloc.c` is the Tcl control surface for SQLite memory tests: raw allocation, deterministic OOM injection, memory status, memdebug logging, page-cache and lookaside configuration, heap configuration, and allocator subsystem swapping.

## Important APIs, types, and functions

`struct MemFault memfault` stores OOM countdown, repeat count, failure counters, benign mode, install state, and saved real allocator. Fault helpers include `faultsimStep()`, `faultsimMalloc()`, `faultsimRealloc()`, `faultsimConfig()`, and `faultsimInstall()`. Tcl commands include `sqlite3_malloc`, `sqlite3_realloc`, `sqlite3_free`, `memset`, `memget`, memory high-water/status commands, memdebug commands, config commands, and `install_malloc_faultsim`.

## Control flow

Fault simulation captures the active allocator, replaces `xMalloc`/`xRealloc`, and installs benign malloc hooks. Each allocation decrements the success countdown or simulates failure, recording first/all faults and benign counts. Tcl commands configure countdown/repeat behavior, inspect pending failures, and exercise `sqlite3_config()`/`sqlite3_db_config()` surfaces.

## State and persistence behavior

State is process-global SQLite configuration plus global test variables. Static buffers support pagecache, heap, and lookaside tests. No schema is persisted, but configuration changes affect later connections and tests.

## Dependencies and integration points

It depends on `sqliteInt.h`, Tcl, hex helpers from `test_hexio.c`, optional `SQLITE_MEMDEBUG`, memsys3/5, and test page-cache hooks. It integrates with OOM loops, leak diagnostics, status accounting, lookaside/pagecache tests, and invalid-config tests.

## Risks and test signals

It rewires global allocation behavior and raw pointer Tcl commands can corrupt memory. A suspicious implementation detail sets `memfault.isInstalled = 1` after both install and uninstall success. Signals include deterministic OOM, benign counters, memory high-water/status triples, backtrace logs, and expected config return codes.
