# sources/storage-engines/sqlite/src/test_init.c

## Purpose

`test_init.c` tests `sqlite3_initialize()` and `sqlite3_shutdown()` behavior when pluggable subsystems fail during initialization. It wraps the memory allocator, mutex implementation, and page-cache implementation with forwarding methods that can deliberately fail.

## Important APIs, types, and functions

Global `wrapped` stores saved `sqlite3_mem_methods`, `sqlite3_mutex_methods`, `sqlite3_pcache_methods2`, init flags, and fail flags. Wrapper families are `wrMem*`, `wrMutex*`, and `wrPCache*`. `installInitWrappers()` captures current methods and installs wrappers. Tcl commands are `init_wrapper_install`, `init_wrapper_query`, `init_wrapper_uninstall`, and `init_wrapper_clear`.

## Control flow

`init_wrapper_install ?mem? ?mutex? ?pcache?` shuts SQLite down, installs wrappers, and marks named subsystems to fail their init method. Successful wrapper init sets a flag; shutdown clears it. `init_wrapper_query` returns the list of subsystems still initialized, letting tests verify partial cleanup and retry semantics.

## State and persistence behavior

All state is process-global SQLite configuration. The file creates no schema or database persistence. `init_wrapper_uninstall` shuts down SQLite and restores the captured original subsystem methods.

## Dependencies and integration points

It depends on `sqliteInt.h`, Tcl, and SQLite global configuration APIs. It integrates with tests for initialization error propagation, subsystem cleanup, and retry after failed init.

## Risks and test signals

It must run before normal initialization or after shutdown; concurrent use can corrupt global configuration. Signals are init return codes, `init_wrapper_query` contents, and successful restoration after uninstall.
