<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_ls.c -->
# sources/user-network-fs/libsmb2/tests/prog_ls.c

Purpose: Directory listing integration test program with optional malloc/calloc failure injection.

Important APIs, types, and functions: Defines interposed `malloc` and `calloc` that fail when `MALLOC_FAIL` or `CALLOC_FAIL` matches the call count, then `usage` and `main` using synchronous libsmb2 connect/opendir/readdir/closedir/disconnect.

Control flow: Parses URL, connects with signing enabled, opens the directory, iterates entries and prints metadata, then cleans up. Allocation wrappers allow shell tests to sweep failure points.

State and persistence behavior: Process-local allocation counters and failure indices are static/global. SMB directory state is owned by libsmb2 and freed by closedir/context destruction.

Dependencies and integration points: Used by basic ls, valgrind, socket-error, and malloc-error shell tests.

Risks: Overriding libc allocation functions is fragile and can fail allocations in unrelated library startup code. The test relies on a live SMB share and specific nonexistent directory behavior.

Test signals: Strong coverage from four ls shell tests including valgrind, LD_PRELOAD socket errors, and ltrace-derived allocation counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_ls.c -->
