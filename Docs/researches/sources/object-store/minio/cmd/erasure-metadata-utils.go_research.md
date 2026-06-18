# sources/object-store/minio/cmd/erasure-metadata-utils.go

Purpose: Provides quorum reducers, metadata readers, disk/metadata shuffling, disk evaluation, deterministic distribution hashing, and multipart part-size calculation for erasure object operations.

Important APIs/types/functions: `counterMap[T].GetValueWithQuorum` returns a value occurring at least quorum times. `reduceCommonVersions` and `reduceCommonDataDir` pick quorum-common metadata version bytes/data dirs. `reduceErrs`, `reduceQuorumErrs`, `reduceReadQuorumErrs`, and `reduceWriteQuorumErrs` convert per-disk error slices into quorum decisions while respecting ignored errors and context cancellation. `diskCount` counts non-nil disks. `hashOrder` creates deterministic 1-based erasure distribution order from a CRC32 of bucket/object key. `readAllFileInfo` reads `xl.meta`/version info in parallel. `shuffleDisksAndPartsMetadataByIndex`, `shuffleDisksAndPartsMetadata`, `shuffleWithDist`, `shufflePartsMetadata`, `shuffleCheckParts`, and `shuffleDisks` align arrays to erasure distribution. `evalDisks` nils disks with corresponding errors. `calculatePartSizeFromIdx` returns expected multipart part size or validation errors.

Control flow and state: Most helpers are pure reducers over slices/maps. `readAllFileInfo` performs concurrent disk I/O through `errgroup.WithNErrs`. Shuffle helpers build new aligned slices and may fall back when metadata consistency is too poor. No persistent state is written directly; these helpers drive later read/write/heal decisions.

Dependencies and integration points: Depends on `StorageAPI.ReadVersion`, `ReadOptions`, `FileInfo`, MinIO error sentinels, `errgroup`, CRC32, and object operation ignored-error lists. Used by read, write, complete multipart upload, and healing paths.

Risks: Quorum reduction correctness directly affects data availability and safety. `reduceErrs` tie-breaking is map-order dependent except for nil preference, so callers must use quorum values that avoid ambiguous correctness. `hashOrder` is 1-based and must match metadata distribution expectations. `reduceCommonVersions` assumes non-empty version byte slices are at least 8 bytes.

Test signals: Covered indirectly by endpoint/healing/common tests and object-layer tests that rely on quorum decisions, distribution shuffling, and part-size calculation.
