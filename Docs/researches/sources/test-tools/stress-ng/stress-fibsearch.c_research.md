# sources/test-tools/stress-ng/stress-fibsearch.c

Purpose: implements `fibsearch`, a CPU/cache/memory search stressor that repeatedly searches a sorted `int32_t` array with a local Fibonacci-search implementation.

Important APIs/types/functions: `fibsearch()` is a generic `bsearch`-like routine taking key, base, member count, element size, and comparator. It computes the smallest Fibonacci number covering the array, narrows the range by comparing at Fibonacci offsets, and returns a matching pointer or `NULL`. `stress_fibsearch()` allocates and initializes the data, invokes `stress_sort_data_int32_init()`, counts comparisons through `stress_sort_compare_get()`, and emits comparison metrics.

Control flow: the stressor reads `--fibsearch-size`, applies minimize/maximize defaults, rounds allocation up to a multiple of eight elements, mmaps the array, synchronizes, and loops. Each iteration fills sorted data, resets comparison counters, searches for every element in the array, optionally verifies the returned pointer value, updates duration/comparison/item counters, and increments bogo operations.

State and persistence behavior: all state is in one anonymous private mapping plus local metric accumulators. No files or durable state are created. The mapping is named `fibsearch-data` and unmapped on exit.

Dependencies and integration points: depends on `core-mmap`, `core-shim`, and `core-sort` helper comparators/counters. Registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`, with optional verification and `fibsearch-size` option.

Risks: the final single-element check compares `key` to `ptr`, unlike the main loop's `ptr` to `key`; this is harmless for equality with the integer comparator but worth preserving in comparator-sensitive refactors. Large `--fibsearch-size` values can consume significant memory and time because every item is searched each iteration.

Test signals: run with minimum, default, and maximum sizes; enable `--verify` to catch search failures; confirm both "comparisons per sec" and "comparisons per item" metrics change with array size and no mmap skip occurs unexpectedly.
