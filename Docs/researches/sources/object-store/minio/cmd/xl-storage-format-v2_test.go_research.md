# sources/object-store/minio/cmd/xl-storage-format-v2_test.go

## Purpose
This hand-written test file validates core XL metadata v2 behavior: partial metadata reads, inline data persistence, transition/restoration data-dir semantics, shared data-dir delete safety, legacy/indexed load compatibility, signature/timestamp repair, quorum version merging, metacache merge integration, healing metadata filtering, and fast `xlMetaBuf` read performance.

## Important APIs, Types, and Functions
The tests directly exercise `readXLMetaNoData`, `xlMetaV2.AddVersion`, `AppendTo`, `Load`, `xlMetaInlineData` operations, `xlMetaV2TrimData`, `xlMetaV2Object.UsesDataDir`, `SharedDataDirCount`, `DeleteVersion`, `mergeXLV2Versions`, `mergeEntryChannels`, `ToFileInfo`, `isIndexedMetaV2`, and `xlMetaBuf.ToFileInfo`. They use `FileInfo`, `ErasureInfo`, lifecycle transition constants, restore header helpers, zstd/zip fixtures, and fixture files under `testdata`.

## Control Flow
`TestXLV2FormatData` builds two inline object versions, serializes/deserializes metadata, checks find/list/remove/replace/rename behavior, trims inline data from the serialized buffer, and confirms metadata CRC corruption is detected. `TestUsesDataDir` checks transitioned, restore-in-progress, restored, expired restore, and normal object cases. `TestDeleteVersionWithSharedDataDir` creates multiple versions sharing or not sharing data dirs and verifies deletion only returns a data dir when no remaining version uses it.

The shallow load tests read a large v1.2 fixture, load legacy metadata, append it as indexed metadata, reload it, and assert header/full-version consistency and sort order. Additional subtests verify historical timestamp/signature repair and compressed index cleanup. Merge tests load multiple fixture metadata copies, mutate headers in controlled ways, and check strict/non-strict quorum behavior. `Test_mergeXLV2Versions2` constructs small synthetic streams and shuffles input order to verify deterministic quorum output. `Test_mergeEntryChannels` verifies higher-level listing merge produces three sorted versions. Benchmarks compare legacy/indexed load, merge, and `ToFileInfo` with/without part details.

## State and Persistence Behavior
The tests encode expected persistence invariants: current metadata can be appended and loaded without losing inline data, inline data can be stripped while retaining readable metadata, indexed headers must match full unmarshaled versions, old metadata must remain readable, and known historical encodings are normalized on load. They also encode lifecycle semantics: transitioned but not restored versions do not require local data-dir deletion; restored versions may use local data; free/hidden markers and delete markers affect listing and merge visibility.

## Dependencies and Integration Points
The file integrates with fixtures (`xl.meta-corrupt.gz`, `xl.meta-v1.2.zst`, `xl-meta-consist.zip`, `xl-meta-merge.zip`, `xl-many-parts.meta`), `metaCacheEntry`, restore header helpers, lifecycle constants, UUID generation, zstd/zip/gzip readers, and the object metadata conversion APIs. This makes it a broad regression suite for storage metadata and list healing behavior.

## Risks and Edge Cases
Several tests use embedded binary/base64 fixtures that are hard to update safely; they are valuable compatibility anchors but can obscure intent. Some coverage is benchmark-only, so performance paths like large-version `UpdateObjectVersion` and many-part `ToFileInfo` are not hard correctness gates unless benchmarks are run. The merge tests cover many header mutations but should be extended whenever `xlMetaV2VersionHeader` fields or non-strict matching rules change.

## Test Signals
Passing tests strongly signal compatibility for v1.2-to-v1.3 load, indexed metadata round-trip, CRC detection, quorum merge selection, data-dir preservation, and inline data operations. Failures in this file usually indicate a real storage compatibility or lifecycle regression and should be treated as high priority.
