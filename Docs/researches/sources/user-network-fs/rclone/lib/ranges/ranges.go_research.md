# sources/user-network-fs/rclone/lib/ranges/ranges.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/ranges/ranges.go -->
## sources/user-network-fs/rclone/lib/ranges/ranges.go

Purpose: represents byte ranges and a sorted, coalesced set of present ranges. This is used by cache/download code to reason about which byte intervals are available, missing, or intersecting.

Important APIs and control flow: `Range` has `Pos`, `Size`, `End`, `IsEmpty`, `Clip`, and `Intersection`. `Ranges` is a slice kept sorted/coalesced by `Insert`, which finds an insertion point with `sort.Search`, merges overlaps or adjacency through `merge`, and removes redundant entries through `coalesce`. `Find` returns the next present or absent segment within a query plus a `next` range for iteration. `FindAll`, `Present`, `Intersection`, `Equal`, `Size`, and `FindMissing` build on `Find`.

State, dependencies, and integration: state is just value slices; no synchronization is provided. The package depends only on `sort`. Integration points include VFS cache/downloaders, where `Ranges` tracks downloaded or written spans.

Risks and test signals: callers must only mutate through `Insert` to preserve invariants. Negative positions/sizes are not explicitly rejected; empty ranges are ignored by insertion and treated as present in `Present`. Boundary behavior is subtle because adjacent ranges merge. Tests in this group extensively exercise insertion, coalescing, searching, intersections, equality, size, random inserts, and missing-range calculations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/ranges/ranges.go -->
