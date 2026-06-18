# sources/storage-engines/pebble/sstable/reader_common.go

## Purpose
`reader_common.go` provides small public aliases and constants shared by SSTable readers and callers. It exposes block and block-iterator transform types through the `sstable` package and defines the filter-block size policy used by point iterators.

## Important APIs, Types, and Functions
- `FilterBlockSizeLimit` is a `uint32` policy controlling whether an existing bloom/filter block may be used.
- `NeverUseFilterBlock` disables filter-block checks.
- `AlwaysUseFilterBlock` allows filter-block use regardless of block size.
- Type aliases re-export `block.BufferPool`, `blockiter.Transforms`, `blockiter.FragmentTransforms`, `blockiter.SyntheticSeqNum`, `SyntheticSuffix`, `SyntheticPrefix`, and `SyntheticPrefixAndSuffix`.
- `NoTransforms` and `NoFragmentTransforms` expose default transform values.
- `MakeSyntheticPrefixAndSuffix` delegates to `blockiter.MakeSyntheticPrefixAndSuffix`.
- `NoSyntheticSeqNum` exposes the zero value that disables synthetic sequence numbers.

## Control Flow
There is no complex control flow. The file establishes names and constants. `MakeSyntheticPrefixAndSuffix` is the only function and simply constructs a combined synthetic prefix/suffix transform value through `blockiter`.

## State and Persistence Behavior
No mutable state is stored. These aliases influence read-time interpretation of persisted keys: synthetic prefix/suffix and synthetic sequence transforms can alter keys surfaced by iterators without modifying the SSTable. `FilterBlockSizeLimit` controls whether persisted filter blocks are consulted.

## Dependencies and Integration Points
- Used by `reader.go` through `IterOptions.FilterBlockSizeLimit`, `NoReadEnv`, and iterator constructors.
- Used by range deletion/key iterator creation through fragment transforms.
- Bridges callers outside `sstable` to lower-level `block` and `blockiter` transform APIs without importing those packages directly.

## Risks and Edge Cases
- `AlwaysUseFilterBlock` is `math.MaxUint32`; a filter block larger than that cannot exist under the type, so all present filters pass the size check.
- Transform aliases expose lower-level semantics; misuse of synthetic transforms can surface keys that differ from persisted bytes, so callers must understand how bounds and virtual SSTables interact.
- These definitions are intentionally thin; behavior changes occur in `blockiter` and iterator code rather than here.

## Test Signals
This file is indirectly covered by iterator, range-key, compaction, and virtual-SSTable tests that pass `NoTransforms`, synthetic transforms, and filter-block policies through `IterOptions`.
