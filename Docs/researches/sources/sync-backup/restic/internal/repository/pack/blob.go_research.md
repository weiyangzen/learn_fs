
# sources/sync-backup/restic/internal/repository/pack/blob.go

Purpose: defines `pack.Blob`, the pack-file header entry used internally by repository indexing and pack parsing. It embeds `restic.BlobHandle` and records encrypted length, offset within the pack data region, and optional uncompressed plaintext length.

Important methods are `String`, `DataLength`, `UncompressedCiphertextLength`, and `IsCompressed`. `DataLength` returns `UncompressedLength` for compressed blobs; otherwise it derives plaintext length from ciphertext length through `crypto.PlaintextLength`. `UncompressedCiphertextLength` computes the ciphertext size that the uncompressed data would occupy, useful for statistics and prune accounting. `IsCompressed` is encoded as nonzero `UncompressedLength`.

State is not persisted directly here, but this struct mirrors pack header entries and index entries. Integration points include pack header creation/parsing, `restic.PackBlob` implementations, repository blob streaming, prune size accounting, and index storage. Risks are correctness of length conversions and the overloaded meaning of zero uncompressed length, especially for zero-size blobs where compression is intentionally not represented.
