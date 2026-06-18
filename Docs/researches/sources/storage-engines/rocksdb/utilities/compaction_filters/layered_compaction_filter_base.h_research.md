# sources/storage-engines/rocksdb/utilities/compaction_filters/layered_compaction_filter_base.h

## Purpose
This header defines a helper base class for compaction filters that wrap or layer behavior on top of a user-provided compaction filter.

## Important APIs, Types, and Functions
`LayeredCompactionFilterBase` derives from `CompactionFilter`. Its constructor accepts either a raw user filter pointer or a `unique_ptr` created by a factory, stores ownership when provided, and chooses the effective `user_comp_filter_`. `user_comp_filter()` returns that inner filter. `Inner()` overrides `Customizable::Inner` so option/introspection tooling can see the wrapped object.

## Control Flow
Construction resolves the inner filter once: if the raw pointer is null, it uses the owned factory-created filter. Runtime calls are expected to be implemented by subclasses that consult `user_comp_filter()`.

## State and Persistence Behavior
The class stores a non-owning pointer plus an optional owning `unique_ptr`. No DB state is modified by this base class itself.

## Dependencies and Integration Points
It depends on RocksDB's compaction filter API and is referenced by layered filters such as blob-index or TTL filters. It integrates with the customizable object tree through `Inner()`.

## Risks and Edge Cases
If both constructor arguments are null, `user_comp_filter_` remains null and subclasses must handle that. The raw pointer is non-owning and must outlive the layered filter unless the owned pointer is used. The base class does not forward any filtering calls itself.

## Test Signals
Coverage should come from concrete layered filters verifying that user filters are invoked, owned factory filters remain alive, and `Inner()` reports the wrapped filter for option introspection.
