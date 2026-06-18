# sources/storage-engines/tikv/components/compact-log-backup/src/compaction/mod.rs

## Purpose
Defines core compaction data structures and module boundaries for collection, execution, and metadata generation.

## APIs and control flow
`Input` records a logical input span plus physical size, compression, CRC, logical KV size, and entry count. `SubcompactionCollectKey` groups files by CF, region, file type, meta flag, and table id. `Subcompaction` holds inputs, size, timestamp range, compact bounds, min/max keys, and region epoch hints; its private `merge` combines same-key groups. `EpochHint` preserves region range and epoch information. `SubcompactionResult` pairs the origin with protobuf output metadata, expected checksum/key/size totals, and load/compact statistics.

`UnformedSubcompaction` is the collector's mutable accumulator. `by_file`, `add_file`, and `form` aggregate file state into a concrete `Subcompaction`. `to_input` converts storage `LogFile` metadata into executable input.

## State, dependencies, and integration
This module owns no persistence directly. It depends on `kvproto::brpb`, bytes, display derivation, storage log metadata, statistics types, and collector config. It re-exports child modules `collector`, `exec`, and `meta`, and constants `SST_OUT_REL` and `META_OUT_REL` define output subdirectories used by executor and checkpoint logic.

## Risks and test signals
`Subcompaction::merge` uses debug assertions for matching keys and compaction bounds, so release builds rely on callers to merge compatible groups. `of_many` panics on empty input and asserts all files have the same collect key. Tests live in child modules and validate grouping, execution, metadata, and epoch hint behavior.
