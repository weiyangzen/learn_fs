# sources/sync-backup/rsync/util2.c

Purpose: smaller utility layer for sleeping, allocation wrappers, checksum formatting, diagnostics, and source-file path shortening.

Important APIs/functions: `msleep()` sleeps milliseconds via `nanosleep`, `usleep`, or `select` fallback. `my_alloc()` backs rsync allocation macros, enforces `--max-alloc`, and supports malloc/calloc/realloc using the sentinel `do_calloc`. `sum_as_hex()` returns canonical digest bytes as hex, reversing order when requested by `canonical_checksum()`. `_out_of_memory()` and `_overflow_exit()` print contextual fatal errors and exit cleanup. `src_file()` strips the source directory prefix from file paths in diagnostics.

Control flow and state: uses global `max_alloc`, static source-prefix cache, and a static hex buffer. Allocation failures either return NULL for nonfatal callers or exit for checked macros.

Dependencies and integration: depends on rsync checksum metadata, logging, cleanup, and memory macros. Risks include static-buffer overwrite in nested `sum_as_hex()` use, integer guard dependence on non-zero `size`, and platform sleep precision. Test signals are broad: allocation overflow paths, diagnostics, and checksum display are exercised indirectly by many rsync modes.
