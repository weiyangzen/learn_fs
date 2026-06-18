# sources/user-network-fs/rclone/lib/ranges/ranges_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/ranges/ranges_test.go -->
## sources/user-network-fs/rclone/lib/ranges/ranges_test.go

Purpose: provides comprehensive table-driven and randomized coverage for the `Range` and `Ranges` algorithms.

Important APIs and control flow: tests cover `End`, `IsEmpty`, `Clip`, single-range intersection, internal `merge`, `coalesce`, `Insert`, random insertion order, `Find`, `FindAll`, `Present`, `Ranges.Intersection`, `Equal`, `Size`, and `FindMissing`. Helpers such as `checkRanges` validate sorted/coalesced invariants and expected contents after operations.

State, dependencies, and integration: tests are in package `ranges`, so they can call unexported helpers like `merge`, `coalesce`, and `search`. Random insertion testing checks algorithm stability across shuffled ranges.

Risks and test signals: this is a strong signal for edge cases around adjacency, partial overlap, nil/empty ranges, and query segmentation. It does not add concurrency tests because the type is a plain slice and expected to be externally synchronized when shared.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/ranges/ranges_test.go -->
