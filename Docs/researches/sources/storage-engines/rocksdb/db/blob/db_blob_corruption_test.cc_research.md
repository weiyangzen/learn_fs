# sources/storage-engines/rocksdb/db/blob/db_blob_corruption_test.cc

## Purpose

This small test file verifies whole-file checksum validation for blob files. It creates blob files with file checksum generation enabled, corrupts the newest blob file on disk, reopens the DB, and asserts `VerifyFileChecksums` reports corruption and triggers the checksum mismatch sync point exactly once.

## Important APIs, Types, and Functions

- `DBBlobCorruptionTest`: `DBTestBase` fixture for blob corruption tests.
- `Corrupt(FileType filetype, int offset, int bytes_to_corrupt)`: scans the DB directory, picks the latest file of the requested type, and corrupts bytes in place with `test::CorruptFile`.
- `VerifyWholeBlobFileChecksum`: test enabling `file_checksum_gen_factory`, writing two blob files, verifying checksums, corrupting one blob file, then validating corruption detection.
- `DBImpl::VerifyFullFileChecksum:mismatch`: sync point used to observe the internal mismatch status.

## Control Flow

The test opens a DB with `enable_blob_files`, `min_blob_size = 0`, and CRC32C file checksum generation. It writes and flushes two blob values, verifies checksums successfully, closes the DB, corrupts bytes at offset zero of the latest `.blob` file, reopens, installs a sync-point callback, and runs `VerifyFileChecksums(ReadOptions())`. The callback counts mismatch events and asserts the status is non-OK.

## State and Persistence Behavior

Persistent state is two flushed blob files with whole-file checksum metadata. The test mutates one blob file after close, then reopens so verification reads the durable corrupted file rather than cached state. No repair is attempted; the expected durable signal is checksum mismatch corruption.

## Dependencies

The file depends on `DBTestBase`, file-name parsing via `ParseFileName`, `test::CorruptFile`, `GetFileChecksumGenCrc32cFactory`, `SyncPoint`, and `VerifyFileChecksums`. It installs the normal RocksDB stack trace handler and custom object registration in `main`.

## Integration Points

This test ties blob files into the DB-wide full file checksum verification API. It ensures blob files are included alongside other file types and that internal mismatch reporting preserves a corruption status visible both through sync points and the public `VerifyFileChecksums` result.

## Risks

- The helper corrupts the latest file of a type, so file numbering and flush behavior must create at least one blob file and leave it in the DB directory.
- Corrupting at offset zero assumes header/checksum validation will detect the change; checksum format changes should preserve that signal.
- Sync-point callback cleanup is required to avoid leaking callbacks into later tests.

## Test Signals

The key signals are an initial successful `VerifyFileChecksums`, successful reopen after corruption, final `VerifyFileChecksums(...).IsCorruption()`, and exactly one invocation of `DBImpl::VerifyFullFileChecksum:mismatch` with a non-OK status.
