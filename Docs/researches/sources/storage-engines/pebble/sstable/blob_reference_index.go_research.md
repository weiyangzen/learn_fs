## sources/storage-engines/pebble/sstable/blob_reference_index.go

Purpose: Maintains and decodes per-blob-reference liveness information for values referenced by an SSTable. It is used while constructing SSTables that refer to blob files, recording which value IDs within each blob value block are still live.

Important APIs/types/functions: `blobReferenceValues` accumulates state for one `base.BlobReferenceID`; `blobRefValueLivenessWriter` owns a dense `refState` slice indexed by reference ID; `addLiveValue` records `(refID, blockID, valueID, valueSize)`; `finish` yields ordered `(refID, encoding)` pairs; `BlobRefLivenessEncoding` and `DecodeBlobRefLivenessEncoding` expose decoded block-level records. The encoding is varint block ID, varint aggregate values size, varint bitmap byte length, then the run-length bitmap bytes produced by `BitmapRunLengthEncoder`.

Control flow: A writer is `init`ed, then live values arrive in monotonically increasing reference IDs and increasing blob block/value order. New reference IDs extend `refState` by exactly one slot; skipped IDs return an assertion error. A change in block ID flushes the current block via `finishCurrentBlock`, starts a new bitmap, and subsequent calls set bits for live value IDs while accumulating value bytes. `finish` flushes every current block and yields all encodings.

State and persistence behavior: State is in-memory until table construction persists the encoded byte slices as blob-reference value liveness index payloads. The dense slice index is part of the contract: reference IDs map directly to slice positions. Encodings are compact, append-only, and corruption-decoded with `base.CorruptionErrorf`.

Dependencies and integration points: Depends on `internal/base` for reference IDs and corruption/assertion errors, `sstable/blob` for blob block/value IDs, `encoding/binary` varints, `iter.Seq2`, `slices.Grow`, and the SSTable bitmap run-length helpers. It integrates with blob-file rewrite/compaction paths that need to know which blob values are live.

Risks: `DecodeBlobRefLivenessEncoding` slices `buf[:enc.BitmapSize]` after parsing bitmap size without an explicit bounds check, so malformed short buffers can panic rather than returning a corruption error. Correctness also depends on caller ordering by reference/block/value ID and on every non-empty current block being flushed exactly once. Calling `finish` repeatedly mutates by appending another copy of the current blocks.

Test signals: Covered by `blob_reference_index_test.go`, including basic multi-value/multi-block encodings, all-live values, and randomized encode/decode/rebuild round trips using `IterSetBitsInRunLengthBitmap`.
