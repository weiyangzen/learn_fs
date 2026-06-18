## sources/storage-engines/pebble/sstable/blob_reference_index_test.go

Purpose: Tests the blob-reference value liveness writer and decoder, verifying byte-level bitmap output and round-trip idempotence.

Important APIs/types/functions: `TestBlobRefValueLivenessWriter` drives `blobRefValueLivenessWriter.init`, `addLiveValue`, `finish`, `DecodeBlobRefLivenessEncoding`, and checks `BlobRefLivenessEncoding` fields. `TestBlobRefLivenessEncoding_Randomized` reconstructs liveness using `IterSetBitsInRunLengthBitmap` and compares re-encoded bytes.

Control flow: The basic subtest writes several values in one reference/block, intentionally leaves gaps in value IDs, advances to another block, decodes the resulting encoding, and checks aggregate `ValuesSize`, `BitmapSize`, and literal bitmap bytes. The all-ones subtest verifies dense value IDs. The randomized test generates increasing reference IDs, increasing block IDs with duplicates, sparse increasing value IDs, encodes, decodes, rebuilds a fresh writer from decoded set bits, and expects byte-for-byte equality.

State and persistence behavior: The tests treat the encoding as stable enough for exact byte comparisons. They also exercise writer reinitialization between rounds, which clears state while preserving capacity.

Dependencies and integration points: Uses `maps.Collect`, Go `iter`, `math/rand/v2`, Pebble `testutils`, `base.BlobReferenceID`, `blob.BlockID`, `blob.BlockValueID`, and `stretchr/testify/require`.

Risks: Randomized coverage is bounded to 20 rounds and does not feed malformed encodings into the decoder, so decode bounds/corruption behavior is not strongly covered. Tests assume ordering constraints rather than proving out-of-order inputs fail cleanly.

Test signals: Strong positive signal for canonical encoding under valid input, sparse bitmap gaps, multiple blocks, and writer re-use.
