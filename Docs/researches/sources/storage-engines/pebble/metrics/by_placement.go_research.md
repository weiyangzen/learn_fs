<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/by_placement.go -->
## sources/storage-engines/pebble/metrics/by_placement.go

Purpose: provides reusable metric containers for count/size accounting by storage placement and file type.

Important APIs and types: `CountAndSizeByPlacement` embeds `ByPlacement[CountAndSize]` with `Inc`, `Dec`, `Accumulate`, `Deduct`, `Total`, `String`, and `SafeFormat`. Generic `ByPlacement[T]` provides `Get`, `Set`, and `Ptr` over `base.Local`, `base.Shared`, and `base.External`. `FileCountsAndSizes` groups table, blob, and other-file counts with aggregate and formatting helpers.

Control flow: placement-specific methods dispatch by `base.Placement`. Invalid placements panic only under invariants builds and otherwise fall back to local. File-type methods send tables and blobs through placement accounting and all other file types through local-only `Other`.

State and persistence: pure in-memory counters used by DB metrics and delete-pacer metrics. No persistence.

Dependencies and integration: depends on `base.Placement`, `base.FileType`, `invariants`, `redact`, and `CountAndSize`. It is consumed by `Metrics.Table.Physical`, `Metrics.BlobFiles`, and delete-pacer summaries.

Risks and edge cases: non-invariants fallback to local can hide invalid placement bugs in production builds. `SafeFormat` for placement only shows local detail when remote/shared counts exist, which is concise but lossy for shared vs external.

Test signals: `by_placement_test.go` covers placement accessors, pointer mutation, inc/dec, accumulation/deduction, totals, and formatted strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/by_placement.go -->
