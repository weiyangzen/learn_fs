# sources/test-tools/stress-ng/stress-judy.c

Purpose: implements `judy`, a Judy array stressor that allocates sparse integer-indexed entries, searches them, deletes them, and records operation rates.

Important APIs/types/functions: `gen_index()` maps dense loop indexes to sparse `Word_t` keys. The Judy macros `JLI`, `JLG`, and `JLD` perform insert, lookup, and delete. Duration/count arrays track insert, find, and delete metrics.

Control flow: `stress_judy()` resolves `judy-size`, sync-starts, then for each iteration creates a fresh JudyL array. It inserts `n` generated indexes with stored values, scans all indexes to find entries and optionally verify stored values, deletes in reverse order, increments bogo ops, and repeats until stopped. On allocation failure it attempts to delete inserted nodes before aborting.

State and persistence behavior: state is contained in the in-memory Judy array and metrics counters. Each loop creates and destroys the array; no filesystem state exists.

Dependencies and integration points: compile-gated on `Judy.h` and libJudy. Uses stress-ng settings, random-free deterministic indexing, metrics, memory pressure messages, and optional verification flag. Registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY`.

Risks: large `judy-size` values stress allocator and may leave partially built arrays if an unexpected macro error path occurs. Verification is optional; without it the stressor mainly exercises library paths and reports rates.

Test signals: run default, min, max, and `--verify`; check insert/find/delete metrics, no Judy allocation errors, and correct `EXIT_NO_RESOURCE` or skip behavior when the library is unavailable.
