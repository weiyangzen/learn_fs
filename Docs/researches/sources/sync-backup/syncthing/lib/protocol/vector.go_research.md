# sources/sync-backup/syncthing/lib/protocol/vector.go

## Purpose
Implements Syncthing version vectors used to compare file versions across devices, merge counters, serialize to wire format, and produce stable string representations.

## Important APIs, Types, and Functions
`Vector` contains sorted `[]Counter`. `Counter` pairs a `ShortID` with a uint64 value. Public methods include `String`, `HumanString`, `ToWire`, `VectorFromWire`, `VectorFromString`, `Update`, `Merge`, `Copy`, `Equal`, `LesserEqual`, `GreaterEqual`, `Concurrent`, `Counter`, `IsEmpty`, `DropOthers`, and `Compare`. `Ordering` has `Equal`, `Greater`, `Lesser`, `ConcurrentLesser`, and `ConcurrentGreater` values.

## Control Flow
`Update` increments an existing counter or inserts/appends a new counter in sorted ID order, using current Unix time as a lower bound. `Merge` walks two sorted vectors and mutates or reallocates `v` to contain maximum counter values. `Compare` performs a two-index merge-like walk, treating missing counters as zero and returning concurrent variants when both greater and lesser evidence is seen. Wire/string conversion loops over counters and encodes IDs big-endian.

## State and Persistence Behavior
Vectors are in-memory value types with slice semantics. Some operations mutate and return the receiver's backing slice when possible; callers needing isolation must use `Copy`. No persistence is performed here, but vector values are serialized into BEP `bep.Vector` messages and stored as part of file metadata elsewhere.

## Dependencies and Integration Points
Depends on `internal/gen/bep`, binary/hex parsing, and `ShortID`. Scanner updates file versions through `Vector.Update`, and model/index logic uses vector comparisons to detect ancestor, equal, and conflict relationships.

## Risks and Edge Cases
Correctness depends on counters being sorted by ID; methods do not sort arbitrary input. Slice aliasing can surprise callers that reuse vectors. `VectorFromString` accepts shortened hex IDs by right-aligning decoded bytes, which is useful but should remain documented. `Update` near `math.MaxUint64` can overflow by adding one, though tests focus on comparison max values rather than update overflow.

## Test Signals
`vector_test.go` covers insertion/update ordering, copy isolation, merge cases, counter lookup, equality/ordering/concurrency, missing zero counters, and maximum uint64 comparison cases.
