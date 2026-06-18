<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_compression.h -->
# sources/storage-engines/rocksdb/include/rocksdb/advanced_compression.h

## Purpose

`advanced_compression.h` declares RocksDB's experimental advanced compression customization API. It separates compression strategy (`Compressor`), decompression schema (`Decompressor`), and manager/factory compatibility (`CompressionManager`), with explicit support for dictionaries, working areas, custom compression type schemas, and wrapper composition.

## Important APIs, Types, and Functions

- `Compressor` defines dictionary guidance/config variants (`DictDisabled`, `DictSampling`, `DictPreDefined`, `DictSamples`, `DictConfig`, `DictConfigArgs`), `WorkingArea`, `ManagedWorkingArea`, cloning/specialization, compression, preferred type, recommended parallelism, serialized dictionary access, and optimized decompressor access.
- `Decompressor` defines working areas, dictionary cloning through `MaybeCloneForDict`, owned-memory reporting, `Args`, `ExtractUncompressedSize`, and `DecompressBlock`.
- `CompressionManager` derives from `Customizable` and `enable_shared_from_this`, exposes `CompatibilityName`, compatibility lookup, string creation, supported type checks, compression-type naming, compressor creation for SST/generic use, and decompressor selection optimized by type set.
- `CompressorWrapper`, `DecompressorWrapper`, and `CompressionManagerWrapper` forward to wrapped implementations for instrumentation or policy layering.
- Factories expose `GetBuiltinV2CompressionManager()`, `CreateAutoSkipCompressionManager()`, and `CreateCostAwareCompressionManager()`.

## Control Flow

A write path asks a `CompressionManager` for a `Compressor` based on options and preferred `CompressionType`. The compressor may recommend dictionary handling for a block role through `GetDictGuidance()`. The caller can collect samples or pass a predefined dictionary into `MaybeCloneSpecialized()`/`CloneMaybeSpecialized()`, then call `CompressBlock()` repeatedly, optionally with a per-thread working area. The compressor returns both bytes and the compression type that must later guide decompression; `kNoCompression` with OK status means compression was declined rather than failed.

A read path gets a compatible `Decompressor` from a manager, optionally optimized for expected types or cloned for a serialized dictionary. It calls `ExtractUncompressedSize()` to parse/strip size metadata and then `DecompressBlock()` into caller-allocated output. Compatibility is mediated by `CompressionManager::CompatibilityName()` so persisted data can be decoded by functionally equivalent managers.

## State and Persistence Behavior

Compression choices become durable because SST/block data stores compressed bytes, compression types, and possibly dictionary blocks. Compatibility names and compression-type mappings must therefore remain stable: expanding support is acceptable, but changing the mapping from type/dictionary/data to output would risk corruption. Compressors for data files are expected to be per-file so strategy can be reconsidered for each file; decompressors without dictionaries can be shared, while dictionary-specific decompressors often reference externally managed dictionary bytes and must not outlive them.

## Dependencies and Integration Points

The API depends on compression type definitions, cache entry roles, data-structure `ManagedPtr`, `CompressionOptions`, `FilterBuildingContext`, and RocksDB customization/config machinery. It integrates with table builders/readers, block compression/decompression, dictionary training, compression manager registry/string creation, and wrapper-based strategy layers.

## Risks and Edge Cases

The file repeatedly warns that exceptions must not escape overridden functions. Dictionary lifetimes are subtle: `MaybeCloneForDict()` clones may reference the supplied `Slice`, so the caller must manage the raw dictionary bytes. `CompressionType` is part of the persisted schema; custom managers must not repurpose types incompatibly under the same compatibility name. `CompressBlock()` OK with `kNoCompression` is not a failure, and callers must correctly fall back to uncompressed data. Working areas are single-thread use even when compressors/decompressors are generally thread-safe.

## Test Signals

Signals include round-trip compression/decompression for every supported type, compatibility lookup by name, dictionary sampling/predefined specialization, serialized dictionary persistence, decompressor clone lifetime tests, working-area reuse and release, wrapper forwarding, `kNoCompression` bypass semantics, corrupt compressed data rejection in `ExtractUncompressedSize()`/`DecompressBlock()`, and SST read/write compatibility across manager instances.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_compression.h -->
