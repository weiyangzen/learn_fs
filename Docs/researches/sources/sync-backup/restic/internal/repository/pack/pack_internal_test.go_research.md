
# sources/sync-backup/restic/internal/repository/pack/pack_internal_test.go

Purpose: tests unexported pack header parsing, footer/header reading, and header verification.

`TestParseHeaderEntry` validates plain and compressed header layouts. `TestParseHeaderEntryErrors` checks invalid type bytes and truncated input. `countingReaderAt` supports `TestReadHeaderEagerLoad`, which asserts when header reading needs one or two random-access reads based on `eagerEntries`. `TestReadRecords` exercises truncation and total-header-size reporting across data/header sizes. `TestUnpackedVerification` damages header plaintext, ciphertext, and length footer to ensure `verifyHeader` detects mismatches or decode failures.

State is in synthetic byte buffers, not a backend, but the tests model persisted pack bytes precisely. Integration risks covered include unnecessary extra backend reads, malformed or oversized headers, compressed header entry sizes, and write-time header corruption detection before upload.
