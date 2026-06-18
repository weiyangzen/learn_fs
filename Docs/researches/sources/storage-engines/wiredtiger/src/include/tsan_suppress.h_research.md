# sources/storage-engines/wiredtiger/src/include/tsan_suppress.h

Purpose: `tsan_suppress.h` provides narrowly named inline wrappers for known benign or transitional data races so WiredTiger can use function-level TSAN suppressions without suppressing entire complex callers.

Important APIs: wrappers cover relaxed loads/stores for integer, bool, size, pointer, and volatile variants; non-atomic add/subtract helpers for selected counters; TSAN-suppressed `memcpy`/`memset`; and typed pointer helpers for `WT_FH`, `WT_PAGE`, `WT_INSERT`, `WT_SESSION_IMPL`, `WT_ADDR`, `WTI_LOGSLOT`, `WT_PAGE_MODIFY`, `WT_PAGE_HEADER`, `WT_UPDATE`, and `const char *`.

Control flow and state: most wrappers call WiredTiger relaxed atomic primitives and return or store a single value. A few add/subtract wrappers intentionally perform plain arithmetic while carrying a suppressible function name. There is no independent state or persistence.

Dependencies and integration points: depends on WiredTiger atomic helpers and forward-declared internal types. It is used by stats, transaction timestamp assignment, update-chain reads, page/ref pointer access, log slot access, cache/page structures, and other hot paths where full synchronization is either pending or intentionally unnecessary for the observed field.

Risks: the file explicitly encodes technical debt. A wrapper can hide a real race if used too broadly, and relaxed atomics do not create ordering guarantees. The plain arithmetic helpers are not atomic despite their suppressive naming. Comments in nearby callers often reference future fixes such as replacing statistic and timestamp races with proper synchronization.

Test signals: TSAN CI with a suppression file that names these wrappers, code review requiring each new wrapper use to document why relaxed/plain access is safe, stress tests around transaction prepare/commit, statistics, page eviction, and log slot handling, plus eventual removal tests when a race is replaced by stronger atomics.
