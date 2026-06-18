## sources/storage-engines/pebble/sstable/blockiter/block_iter.go

Purpose: Defines common interfaces for row-block and columnar-block data/index iterators, allowing SSTable iterators to abstract over block engine implementations.

Important APIs/types/functions: `Data` interface covers point-block iteration (`SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextWithSamePrefix`, `NextPrefix`, `Prev`, `KV`, `Valid`, `Error`, `Close`), buffer-handle ownership (`Handle`, `InitHandle`, `Invalidate`, `IsDataInvalidated`), lower-bound proof, and `treesteps.Node`. `Index` covers index block initialization, block-handle ownership, separator comparisons, `BlockHandleWithProperties`, seeking/stepping, invalidation, close, and `treesteps.Node`.

Control flow: There is no implementation here; the interfaces define contracts. Important contracts include `SeekPrefixGE`/`NextWithSamePrefix` positioning semantics when prefix mismatches occur, ownership transfer/release of `block.BufferHandle` on `InitHandle` and `Close`, and best-effort `IsLowerBound` behavior.

State and persistence behavior: State is implementation-defined in row/column iterators. The interface influences durable decoding because `Index.BlockHandleWithProperties` must parse encoded handles plus block properties from index entries.

Dependencies and integration points: Implemented by `rowblk.Iter`, `colblk.DataBlockIter`, `rowblk.IndexIter`, and `colblk.IndexBlockIter`. Used by higher-level SSTable iterators, table format dispatch, block-property filtering, and tree-step debugging.

Risks: The contracts are subtle around invalidation versus current KV validity, prefix mismatch positioning, and buffer-handle ownership. Implementations must release handles even on reinitialization/error to avoid leaks.

Test signals: No direct tests here; concrete row/column iterator tests elsewhere validate conformance. `block_property_test.go` indirectly uses `Index.BlockHandleWithProperties`.
