# sources/storage-engines/pebble/sstable/rowblk/rowblk_index_iter.go

## Purpose
This file defines `IndexIter`, a lightweight adapter that makes the row-block `Iter` satisfy Pebble's `blockiter.Index` interface. It is used to iterate row-oriented SSTable index blocks, exposing separators and encoded block handles to higher-level table iterators.

## Important APIs, Types, And Functions
`IndexIter` contains one embedded row-block `Iter`. `Init` initializes it from a raw block byte slice; `InitHandle` initializes it from a `block.BufferHandle`. `Valid`, `IsDataInvalidated`, `Invalidate`, `Handle`, and `Close` expose lifecycle and validity state. `Separator`, `SeparatorLT`, and `SeparatorGT` expose comparator-based separator operations. `BlockHandleWithProperties` decodes the current value with `block.DecodeHandleWithProperties`. `SeekGE`, `First`, `Last`, `Next`, and `Prev` adapt row-block iterator positioning to boolean index-iterator semantics. `TreeStepsNode` delegates tracing to the underlying iterator.

## Control Flow
The adapter is intentionally thin. Positioning calls invoke the corresponding row-block iterator method and return whether a KV was found. Separator methods read the current internal key's user key. Block handle decoding reads the current in-place value. Invalidation and close delegate directly to the inner iterator.

## State And Persistence Behavior
`IndexIter` owns no persistent data. It holds references to the block data or buffer handle managed by the inner `Iter`. `Invalidate` drops those references through the inner iterator, and `Close` releases resources through `Iter.Close`. Validity is determined by the inner restart offset range rather than by the full point-iterator `Valid` contract.

## Dependencies And Integration Points
This adapter is the row-block implementation behind table-format `newIndexIter` calls and is used by both single-level and two-level SSTable iterators. It depends on row-block `Iter`, `base.Comparer`, `block.BufferHandle`, `block.HandleWithProperties`, `blockiter.Transforms`, and `treesteps`.

## Risks
Because it is a thin adapter, the main risks are semantic mismatches: `Valid` must reflect index-entry positioning, separators must be compared with the same comparator used to build the index, and values must always encode block handles with optional properties. Any change to row-block iterator validity internals or index block value encoding can break this adapter.

## Test Signals
Coverage is mostly indirect through reader tests, two-level iterator tests, index layout printing, checksum validation, and benchmarks. Any failure to seek across data blocks, load second-level index blocks, decode handles, or print index layout can implicate this adapter.
