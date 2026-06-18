<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/by_placement_test.go -->
## sources/storage-engines/pebble/metrics/by_placement_test.go

Purpose: verifies placement-aware and file-type-aware metric arithmetic and safe formatting behavior.

Important APIs and functions: tests cover `CountAndSizeByPlacement.Get`, `Ptr`, `Inc`, `Dec`, `Accumulate`, `Deduct`, `Total`, plus `FileCountsAndSizes.Inc`, `Dec`, `Accumulate`, `Deduct`, `Total`, and `String`.

Control flow: each test constructs small explicit counters and checks exact structs after operations. String tests use table-driven cases for empty metrics, local-only tables, shared tables, blob files, other files, and combinations.

State and persistence: no persistent state; only pure metric structs.

Dependencies and integration: depends on `base.FileType`, `base.Placement`, `CountAndSize`, `CountAndSizeByPlacement`, and `testify/require`.

Risks and gaps: invalid placement behavior under invariants is not tested here. Underflow behavior is mostly delegated to `CountAndSize` and covered by its tests, not specifically by placement wrappers.

Test signals: direct unit coverage locks down arithmetic and user-facing string summaries such as `tables: 5 (1KB) [local: 3 (512B)]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/by_placement_test.go -->
