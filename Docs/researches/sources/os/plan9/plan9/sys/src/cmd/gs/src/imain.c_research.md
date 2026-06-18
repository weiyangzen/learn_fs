# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imain.c

Provides common top-level support for Ghostscript interpreter front ends.

Key points:
- `get_minst_from_memory` retrieves the interpreter instance through library context backpointers.
- `gs_main_alloc_instance` allocates and initializes `gs_main_instance`.
- `gs_main_init0` performs platform setup, resets debug flags, records base time, and allocates library path containers.
- `gs_main_init1` initializes interpreter allocator spaces, library level 1, save machinery, name table, object dictionaries, and plugins.
- `gs_main_init2` runs operator initialization, initializes IO devices, publishes `INITFILES`/`EMULATORS`/`LIBPATH`, runs init files or compiled init string, sets display callback, and initializes readline.
- `gs_main_interpret` wraps `gs_interpret` and handles `e_NeedStdin`, `e_NeedStdout`, and `e_NeedStderr` callouts.
- Provides search path helpers, file/string execution helpers, suspendable string input, operand stack C API, stack dumping, resource usage, and exit/abort helpers.
- `gs_main_finit` collects temp filenames, performs final reclaim, closes devices/files, finalizes readline/plugins/library state, restores allocations, and unlinks temp files.

Research relevance:
- Main lifecycle engine for embedding, running, and finalizing the Ghostscript interpreter.
