# sources/test-tools/fio/t/stest.c

Purpose: standalone stress test for fio's smalloc allocator. It repeatedly allocates random small buffers up to an aggregate limit, verifies zeroed memory from `scalloc()`, checks list/magic integrity, frees entries, and interleaves larger allocations during the free phase.

Important APIs and types: `struct elem` stores guard magic values, an intrusive `flist_head`, and allocation size. `do_rand_allocs()` drives allocation/free validation. It uses fio internal `scalloc()`, `sfree()`, `sinit()`, `smalloc_debug()`, `cleanup()`, `flist` helpers, `arch_init()`, and `debug_init()`.

Control flow: `main()` initializes architecture, smalloc, and debug state, calls `do_rand_allocs()`, prints smalloc debug information, cleans up, and returns the error count. `do_rand_allocs()` repeats `LOOPS` rounds, optionally reseeds with `STEST_SEED`, fills a global list until `MAXSMALLOC`, validates zero fill, assigns magic markers, then frees while checking magic and trying `LARGESMALLOC` allocations.

State and persistence: all state is in smalloc-managed memory and a static list. No files are written. The allocator global state is initialized and cleaned in-process.

Dependencies and integration points: built against fio internals (`smalloc.h`, `flist.h`, `arch.h`, `debug.h`). It is registered in `run-fio-tests.py` as executable test 1005 with `SUCCESS_STDERR`.

Risks and test signals: assertions catch list corruption, while explicit checks count allocation failure and non-zeroed memory. The test is memory intensive, up to roughly 120 MiB per round plus large allocation probes. Success is zero return status, expected diagnostic output, and no assertion abort.
