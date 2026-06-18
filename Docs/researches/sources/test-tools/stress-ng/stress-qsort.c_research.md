# sources/test-tools/stress-ng/stress-qsort.c research

Purpose: implements `qsort`, a CPU/cache/memory sort stressor that sorts arrays of 32-bit integers with either libc `qsort` or stress-ng's Bentley-McIlroy implementation.

Important APIs, types, and functions: `stress_qsort_method_t` maps method names to `qsort_func_t`; comparators and data initializers come from `core-sort`. `stress_qsort_verify_forward()` and `stress_qsort_verify_reverse()` check ordering when verification is enabled. A `SIGALRM` handler uses `siglongjmp` to escape long sort calls.

Control flow: `stress_qsort()` resolves size and method, mmaps the integer array, installs optional longjmp-based alarm handling, initializes deterministic sort data, synchronizes, then repeatedly shuffles, forward sorts, verifies, reverse sorts, verifies, mangles data, and sorts again. It tracks comparator count, sorted item count, duration, and bogo ops, then emits comparisons/sec and comparisons/item metrics.

State and persistence: array data is anonymous private memory; signal jump state is process-global and restored on exit. No persistent files are used.

Dependencies and integration: requires stress-ng mmap, madvise collapse, signal, sort helpers, target clone support, and optional libc `qsort`. It is `VERIFY_OPTIONAL` and classified as hot CPU/cache/memory/sort work.

Risks: asynchronous longjmp from signal context must restore the previous `SIGALRM` handler, and metrics can be skewed if interrupted. Verification is optional, so default runs mainly measure load unless `--verify` is set. Large arrays can pressure memory and caches.

Test signals: method selection log, optional ordering failures, signal interruption cleanup, comparisons metrics, and successful unmap are the main signals.
