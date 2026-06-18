<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/options.go -->
# sources/sync-backup/kopia/tests/tools/fio/options.go

This file defines FIO option builders. `Options` is a string map with `Merge` plus fluent methods for size, size ranges, I/O limits, file counts, file-size ranges, dedupe percentage, block size, fallocate mode, randrepeat, and directory.

Control flow is immutable-style: each builder returns a merged map, preserving the original input. `rangeOpt` swaps min/max if needed and formats `min-max`; `boolOpt` converts booleans to `1`/`0`.

There is no persistent state. Integration is broad: `fiofilewriter` uses these builders to construct randomized workloads, and `Runner` turns maps into CLI args. Risks include int narrowing from int64 to int, map iteration nondeterminism, and missing validation for unsupported FIO values. Unit tests cover workload/config option behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/options.go -->
