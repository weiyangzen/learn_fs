# sources/storage-engines/pebble/sstable/colblk/uints_test.go

## Purpose
Tests encoding choice, serialized layout, builder operations, and randomized round-trips for compact uint columns.

## Important APIs, Types, and Functions
- `TestByteWidth` covers width thresholds from zero through `math.MaxUint64`.
- `BenchmarkByteWidth` measures the precomputed table path.
- `TestUintEncoding` checks `DetermineUintEncoding` and small-row delta avoidance.
- `TestUints` is a datadriven state machine for init, write, get, size, and finish/format commands.
- `TestUintsRandomized` compares builder output against `DecodeUnsafeUints` for randomized row counts and values.

## Control Flow
The datadriven test mutates a single `UintBuilder` across commands, allowing tests of reset/default-zero behavior and partial finishes. Randomized tests build expected value slices, optionally leave default-zero rows unset, serialize, decode, and compare each row.

## State and Persistence Behavior
The test validates serialized size and binary formatting at arbitrary offsets, which exercises alignment padding. It also checks `InitWithDefault` semantics where encoded rows can be greater or fewer than explicitly set rows.

## Dependencies and Integration Points
Uses `datadriven`, `crbytes.AllocAligned`, `binfmt`, `treeprinter`, `require`, and `DecodeUnsafeUints`. It relies on shared `interestingIntRanges` for expected encodings.

## Risks and Edge Cases
Randomized seed is time-based and logged, so failures are reproducible manually but not deterministic by default. The suite explicitly targets row-count thresholds where delta-base overhead changes the best encoding.

## Test Signals
High-value coverage for boundary values, partial-prefix finishing, offset alignment, default-zero operation, and decoder compatibility.
