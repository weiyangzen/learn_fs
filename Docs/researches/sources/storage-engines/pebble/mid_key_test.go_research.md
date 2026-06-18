<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/mid_key_test.go -->
## sources/storage-engines/pebble/mid_key_test.go

Purpose: integration test for approximate disk-usage bisection by key.

Important APIs and functions: `TestApproximateMidKey` opens a MemFS Pebble DB with compression disabled and automatic compactions disabled, writes structured key ranges, then calls `ApproximateMidKey` for multiple scenarios.

Control flow: the test creates one large single-SST `b` range, four flushed L0 `c` SSTs, a `d` range split across L6 and L0 through compaction plus later flush, and a tiny `e` range. Cases assert nil for empty and tiny spans, and non-nil interior mid keys for single-SST, multiple-SST, multiple-level, and tight-epsilon ranges. For non-nil keys it estimates left and right disk usage and checks the left fraction is between 15% and 85%.

State and persistence: uses an in-memory DB but real flush/compaction state and SST index structures. Random 4KB values encourage one data block per key, improving index-block bisection coverage.

Dependencies and integration: integrates `ApproximateMidKey`, `EstimateDiskUsage`, flush/compaction, SST indexing, comparer ordering, and vfs MemFS.

Risks and gaps: thresholds are intentionally broad, so precision regressions within the 15%-85% band may pass. It does not test invalid range error handling or context cancellation during index reads.

Test signals: good coverage for the main algorithmic branches: no data, too small for epsilon, coarse SST-boundary split, merge-walk refinement, and multi-level overlap.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/mid_key_test.go -->
