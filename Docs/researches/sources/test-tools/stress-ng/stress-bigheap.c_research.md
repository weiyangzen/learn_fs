<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bigheap.c -->
# sources/test-tools/stress-ng/stress-bigheap.c

Purpose: `stress-bigheap.c` implements the `bigheap` VM/OS stressor. It grows heap allocations with `malloc`, `calloc`, and `realloc`, optionally locks future mappings, writes and verifies pointer patterns, and runs inside an OOM-manageable child.

Important APIs/types/functions: options are `bigheap-bytes`, `bigheap-growth`, and `bigheap-mlock`. Phase constants name the current allocation/check stage and feed `stress_bigheap_phase()`. `stress_bigheap_segvhandler()` records fault signal data and longjmps out. `stress_bigheap_child()` owns allocation growth, low-memory avoidance, optional `malloc_trim()`, aggressive-mode extra realloc/calloc behavior, page/full-heap writes, optional verification, metrics, and cleanup. `stress_bigheap()` wraps the child with `stress_oomable_child()`.

Control flow: the child installs a SIGSEGV handler, resolves options with maximize/minimize behavior, rounds growth to page size, syncs, optionally `mlockall(MCL_FUTURE)`, then repeatedly grows or resets the allocation. When the configured byte limit or low-memory check is reached it frees and restarts from zero. Successful allocations are filled with their own addresses at page or pointer stride, optionally verified, and counted. Allocation failures reset size and continue unless a signal is caught.

State and persistence behavior: no files are persisted. State is heap memory, `phase`, fault metadata, last allocation address/end, and metrics for realloc calls. `malloc_trim(0)` may return heap pages to the allocator/system when available.

Dependencies and integration points: uses stress-ng OOM child handling, memory-free reporting, signal longjmp, process states, option parsing, `malloc_trim` feature checks, `mlockall`, and metrics. It registers `VERIFY_OPTIONAL` and is unimplemented without siglongjmp support.

Risks: pointer-pattern verification can fault if allocator metadata or overrun bugs are introduced, which is intentional but makes signal reporting critical. `bigheap_growth` is stored as `uint64_t` then rounded with page-size arithmetic; bounds and overflow should remain guarded by option parsing. OOM handling may mask allocation stress behavior depending on global flags.

Test signals: use low byte limits, high growth, aggressive mode, `bigheap-mlock`, verify mode, and OOM-avoid flags. Regression signals include SIGSEGV phase reports, verify mismatch messages, skip on allocation failure, and the `realloc calls per sec` metric.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bigheap.c -->
