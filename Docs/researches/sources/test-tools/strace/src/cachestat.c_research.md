<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/cachestat.c -->
## sources/test-tools/strace/src/cachestat.c

Purpose: Decodes the `cachestat` syscall, printing the input range on entry and cache statistics on exit.

Important APIs and types: `SYS_FUNC(cachestat)`, `struct cachestat_range`, and `struct cachestat`.

Control flow: On entry, prints `fd` with `printfd` and fetches `cstat_range` from the tracee to print `off` and `len`. On exit, fetches `cstat` and prints `nr_cache`, `nr_dirty`, `nr_writeback`, `nr_evicted`, and `nr_recently_evicted`, then prints raw `flags`.

State and persistence: No stored state; relies on syscall phase to split input and output fields.

Dependencies and integration: Depends on `defs.h` and local `cachestat.h`. Uses generic memory fetch and field print helpers.

Risks: Flags are printed numerically because no xlat table is used. If the kernel extends structures, this decoder will not show new fields until updated.

Test signals: Tests should include valid pointers, null/unreadable pointers, successful exits, failed exits, and non-zero flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/cachestat.c -->
