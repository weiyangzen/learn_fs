# sources/security-integrity/cryfs/crates/utils/src/testutils/asserts.rs

Purpose: Provides test assertion helpers for unordered vector equality and byte-slice range equality with clearer failure output than raw `assert_eq`.

Important APIs and types: `assert_unordered_vec_eq<T: Eq + Ord + Debug>` sorts both vectors, compares them, and reports `both`, `left only`, and `right only` partitions on mismatch. `assert_data_range_eq` applies a `RangeBounds<usize>` to two byte slices and compares the selected ranges. Private helpers are `difference_partition` and `_apply_bound`.

Control flow: The unordered assertion sorts inputs, then if they differ calls `difference_partition`, which retains only elements absent from the right side while removing matched right-side entries into `both`. Range comparison translates inclusive, exclusive, and unbounded bounds to slice indices, then slices both buffers.

State and persistence behavior: There is no persistence. Both unordered inputs are consumed and sorted, and `difference_partition` destructively removes matching right-hand elements to preserve duplicate-count semantics.

Dependencies and integration points: Used by tests elsewhere in CryFS utilities. It depends only on standard `Debug`, `RangeBounds`, and `Bound`.

Risks: Sorting means `T` must implement `Ord`, even though difference partition itself only needs equality. `_apply_bound` lets normal slice indexing panic on out-of-range or invalid ranges; this is acceptable for assertion helpers but should not be used as validation logic. Duplicate reporting is count-aware but not optimized for large vectors because it linearly searches the right side.

Test signals: Unit tests exercise empty inputs, left-only, right-only, both sides, mixed partitions, and duplicate element accounting. There are no explicit tests for `_apply_bound` range variants in this file.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/testutils/asserts.rs` completely for this pass (155 lines, 5240 bytes).
