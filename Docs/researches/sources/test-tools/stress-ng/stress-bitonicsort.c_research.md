<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bitonicsort.c -->
# sources/test-tools/stress-ng/stress-bitonicsort.c

Purpose: `stress-bitonicsort.c` implements the `bitonicsort` CPU/cache/memory sort stressor for 32-bit integer arrays. It performs forward and reverse bitonic sorts and optional order verification.

Important APIs/types/functions: options include `bitonicsort-size`. `bitonicsort32_fwd()` and `bitonicsort32_rev()` implement compare/swap networks over the full array, updating global `bitonic_count`. Optional `stress_bitonicsort_handler()` uses `siglongjmp` on `SIGALRM` for graceful timeout escape. The main `stress_bitonicsort()` allocates data with `stress_mmap_populate()`, initializes/shuffles/mangles data through `core-sort`, and emits comparison metrics.

Control flow: after resolving size with maximize/minimize overrides, the stressor mmaps the data array, optionally installs the alarm longjmp handler, initializes sorted data, syncs, then loops. Each iteration shuffles data, forward sorts and verifies ascending order, reverse sorts and verifies descending order, mangles data, reverse sorts again, verifies, and increments bogo operations.

State and persistence behavior: no persistent state exists beyond the anonymous mapping. Runtime state includes the data array, `bitonic_count`, optional jump buffer flag `do_jmp`, and comparison/duration counters. The mapping is named and advised for collapse/hugepage behavior when supported.

Dependencies and integration points: depends on `core-sort` data generation/comparison helpers, mmap/madvise helpers, signal wrappers, option parsing, sync barriers, process states, and metrics. It is registered with `VERIFY_OPTIONAL`.

Risks: bitonic sort algorithms generally assume power-of-two element counts for full correctness, while `bitonicsort-size` is a byte-like numeric option without obvious power-of-two rounding. Non-power-of-two sizes may expose ordering issues. Longjmp cleanup must restore the previous alarm handler and unmap data.

Test signals: run minimum, default, maximum, and non-power-of-two sizes with verify enabled. Check forward/reverse order failure messages, timeout behavior via `SIGALRM`, skip on mmap failure, and metrics `bitonicsort comparisons per sec` and `bitonicsort comparisons per item`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bitonicsort.c -->
