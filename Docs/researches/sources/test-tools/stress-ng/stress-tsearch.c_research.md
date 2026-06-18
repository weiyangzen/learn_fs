# sources/test-tools/stress-ng/stress-tsearch.c

## Purpose
Implements the `tsearch` stressor, a libc tree-search workload that inserts shuffled 32-bit integers with `tsearch()`, searches them with `tfind()`, deletes them with `tdelete()`, and records comparison metrics.

## Important APIs, Types, And Functions
The stressor uses `search.h` APIs `tsearch`, `tfind`, and `tdelete`, plus stress-ng sort helpers for deterministic data initialization, shuffling, forward integer comparison, and comparison counting. The only option is `tsearch-size`, defaulting to 64 KB integers with min/max overrides.

## Control Flow
`stress_tsearch()` resolves size, allocates an `int32_t` array, waits at the sync barrier, initializes the data set, then loops while successful and running. Each iteration shuffles data, inserts every element into a fresh libc tree, aborts with cleanup if a tree node cannot be allocated, resets comparison counters, times a find pass across the array, optionally verifies that each found pointer exists and matches the requested value, accumulates comparison count and searched item count, deletes every inserted value, and increments bogo ops. On exit it emits comparisons/sec and comparisons/item metrics and frees the data array.

## State And Persistence Behavior
Data lives in heap memory, and the libc tree root is local to each loop iteration. Tree nodes allocated internally by `tsearch()` are released through `tdelete()` for inserted values. No files or kernel objects persist.

## Dependencies And Integration Points
The implemented path requires `search.h` and `tsearch()`. It uses stress-ng option parsing, sort data helpers, compare counters, timing, metrics, sync, and proc-state helpers. Metadata registers `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`, `VERIFY_OPTIONAL`; unsupported builds export an unimplemented reason.

## Risks And Test Signals
If insertion fails partway through, the code deletes values inserted so far and jumps to metric/cleanup handling. Duplicate values may cause `tsearch()` to return existing nodes, but the initialized data set is intended for searchable integer coverage. Verification checks pointer existence and value equality, but default non-verify runs primarily measure comparison behavior. Test signals include allocation skip/failure paths, optional element mismatch logs, bogo progress, comparisons/sec metric, comparisons/item metric, and clean unimplemented registration without libc support.
