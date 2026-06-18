# `sources/test-tools/filebench/stats.c`

Purpose: Collects, rolls up, clears, and reports Filebench runtime statistics for flowops and global I/O categories.

Important APIs and functions: Public functions are `stats_clear()` and `stats_snap()`. Static `stats_add()` accumulates counts, byte counters, total latency, min/max latency, and OS profile latency distribution buckets. `globalstats` is a heap-allocated array indexed by Filebench flow type.

Control flow: `stats_clear()` allocates `globalstats` if missing, zeros global and per-flowop stats, and records `fs_stime`. `stats_snap()` refuses to run before clear or after abort-error, sets `shm_bequiet` to freeze updates, preserves the original start time, zeros global and master flowop stats, sets end time, iterates runtime flowops, rolls each into both type-specific and global totals, rolls each into its `FLOW_MASTER` flowop by name, builds a per-operation text breakdown, optionally includes histogram buckets, emits the I/O summary, then clears `shm_bequiet`.

State and persistence: Stats are in memory only. Per-flowop counters live in each `flowop->fo_stats`; aggregate state is in `globalstats`. `shm_bequiet` is a shared flag used to reduce concurrent mutation during snapshotting.

Dependencies and integration: Depends on `flowop_find_one()`, `filebench_shm->shm_flowoplist`, `filebench_log()`, `gethrtime()`, `vars`, and `fbtime` conversion constants. It integrates with the scripting command layer through `stats clear` and `stats snap` behavior.

Risks and test signals: The 1 MiB string buffer uses repeated `strcat()` and can overflow if there are many flowops or large histograms. `stats_clear()` zeros only `sizeof(struct flowstats)` after already zeroing `FLOW_TYPES`, which is harmless but redundant-looking. Snapshot accuracy depends on cooperative `shm_bequiet`, not a full lock. Tests should verify summaries for read/write/AIO flowops, latency min/max initialization, histogram output, abort-error suppression, and repeated clear/snap cycles.
