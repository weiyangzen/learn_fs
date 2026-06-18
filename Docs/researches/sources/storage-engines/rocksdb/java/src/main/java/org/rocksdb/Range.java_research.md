# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Range.java

## Purpose
`Range` is a minimal Java value holder representing a half-open RocksDB key range from `start` to `limit`. It is used where Java APIs need to pass key ranges to native RocksDB operations.

## Important APIs, Types, And Functions
- Fields: package-private final `Slice start` and `Slice limit`.
- Constructor `Range(Slice start, Slice limit)` stores both slice references as provided.

## Control Flow
Construction is the only logic. The class does not validate ordering, nullability, or ownership. Native-call sites or higher-level API methods are responsible for interpreting the range.

## State And Persistence Behavior
The object holds Java references to `Slice` objects, which may themselves own native memory. The fields are final, so the range cannot be reseated after construction, but the underlying slice/native lifetime remains external. The class deliberately exposes representation to same-package JNI bridge code.

## Dependencies And Integration Points
- Depends on `Slice`, RocksDB's Java wrapper around native `rocksdb::Slice`.
- SpotBugs excludes `Range` from `EI_EXPOSE_REP2`, acknowledging that it stores externally supplied mutable/native-backed representation.
- Likely integrated by APIs that convert Java range lists into native `Slice` start/limit arrays for size/property/range operations.

## Risks And Edge Cases
- No null checks: a null `start` or `limit` can fail later in JNI conversion.
- No copy: caller disposal of either `Slice` can leave a range with stale native handles.
- No comparator/order validation: inverted ranges are allowed at construction and must be rejected or handled downstream.

## Test Signals
- The source itself has no dedicated tests visible in this subset.
- Meaningful tests should cover APIs consuming `Range`, especially native conversion, null handling, slice lifetime, and correct half-open semantics.
