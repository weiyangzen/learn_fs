# sources/storage-engines/rocksdb/db/db_encryption_test.cc

## Purpose

`db_encryption_test.cc` is a compact RocksDB GoogleTest suite for encrypted environment integration. It verifies that user keys and values are not visible in raw files when the test fixture is running with an encrypted environment, that empty encrypted/plain files can be read safely, and that RocksDB can operate when encrypted random-access files do not implement `GetFileSize()`.

The file is a DB-level integration test rather than encryption algorithm code. Its main purpose is to validate the environment/file-system wrapper contract used by encrypted RocksDB builds.

## Important APIs, Types, and Helpers

- `DBEncryptionTest : public DBTestBase` uses the test DB name `db_encryption_test` with `env_do_fsync=true`.
- `GetNonEncryptedEnv()` returns the underlying target environment when `encrypted_env_` is present by casting it to `CompositeEnvWrapper` and calling `env_target()`. Otherwise it returns the fixture `env_`.
- Tests use DB helpers `Put`, `Close`, `CurrentOptions`, `dbname_`, `env_`, and `encrypted_env_` from `DBTestBase`.
- File APIs include `Env::GetChildren`, `Env::NewSequentialFile`, `Env::GetFileSize`, `SequentialFile::Read`, `EnvOptions`, `WritableFile`, `FileSystem::NewRandomAccessFile`, `FSRandomAccessFile::GetFileSize`, `FileOptions`, and `CreateFile`.
- Status expectations use `ASSERT_OK`, `ASSERT_TRUE(status.IsNotSupported())`, `ASSERT_EQ`, and `ASSERT_GE`.
- The test includes `rocksdb/perf_context.h` and `test_util/sync_point.h`, although the visible tests do not use performance counters or sync points directly.

## Control Flow and State Behavior

`CheckEncrypted` writes two recognizable key/value pairs, closes the DB, enumerates the DB directory, and opens every file except `LOCK` through the non-encrypted target environment. It reads each file's raw bytes and searches for the inserted keys, full values, and one value substring. If the fixture has `encrypted_env_`, no hits are allowed; otherwise at least four hits are expected. This creates a dual-mode test: encrypted builds prove plaintext is hidden in storage files, while non-encrypted builds prove the scan would have detected the markers.

`ReadEmptyFile` creates an empty file through the non-encrypted/default environment, reopens it as a sequential file, and reads 16 bytes into a scratch buffer. The expected behavior is `Status::OK` with an empty `Slice`. The comment documents the regression target: reading from an empty file must not trigger an assertion in the file wrapper.

`NotSupportedGetFileSize` only runs when `encrypted_env_` exists. It obtains the encrypted file system, creates an empty file, opens it as an `FSRandomAccessFile`, calls `GetFileSize()`, and asserts the method returns `NotSupported`. The test documents that RocksDB DB operation should not depend on encrypted `FSRandomAccessFile::GetFileSize()` support because table footer reading can fall back to the file system-level `GetFileSize()`.

## State and Persistence Behavior

Persistent state under test is the DB directory contents after a small write workload and the raw bytes stored in generated files. The key security property is that plaintext keys and values written through the DB are not recoverable by opening the physical files through the underlying non-encrypted environment.

The test deliberately closes the DB before scanning files, ensuring memtable/WAL/table data have reached stable file state visible to `Env::GetChildren`. It skips `LOCK` because that file is not expected to contain user records and may be special to the environment.

For empty files, the state contract is simpler: a zero-byte file must read as an empty slice without assertion, both through regular sequential access and through encrypted filesystem random-access setup. The `NotSupportedGetFileSize` case also verifies a negative capability contract: an encrypted random-access file may reject direct file-size queries while the surrounding DB/table code remains expected to use a fallback path.

## Dependencies and Integration Points

The suite integrates `DBTestBase` encrypted-environment fixture support with RocksDB's `Env` and newer `FileSystem` APIs. It depends on `CompositeEnvWrapper` to expose the target non-encrypted environment for raw-file inspection and on encrypted file wrappers to hide plaintext while still preserving DB readability.

Important integration points are:

- Encrypted environment setup in the broader test harness through `encrypted_env_`.
- Raw file enumeration and sequential reads through the underlying environment.
- `FSRandomAccessFile` capability handling, especially `GetFileSize()` returning `NotSupported`.
- Table footer reading behavior outside this file, where `ReadFooterFromFile()` is expected to fall back to file-system-level size queries.

## Risks and Edge Cases

`CheckEncrypted` is a coarse plaintext scan, not a cryptographic verification. It catches obvious unencrypted leakage of the inserted strings, but it does not prove encryption strength, nonce/key correctness, or absence of all metadata leakage.

The raw read uses `scratch.reserve(fileSize)` and then passes `scratch.data()` as the destination buffer. In modern C++, writing into reserved but not resized string storage is risky because the string size remains zero and writable capacity through `data()` is only well-defined for existing characters. The test then relies on the returned `Slice` for length, but the scratch buffer lifetime and writable range still make this a maintenance hazard if standard/library behavior changes.

The test assumes plaintext markers should appear in non-encrypted mode. Changes to file format, compression, WAL flushing, table encoding, or write path could reduce visible hits and make the non-encrypted sanity branch flaky even though the DB is correct.

The encrypted `GetFileSize()` negative capability is intentional. Production code must continue to tolerate `NotSupported` from `FSRandomAccessFile::GetFileSize()`; adding unconditional direct size calls in table readers would regress encrypted environments.

## Test Signals

Strong signals include zero plaintext marker hits when `encrypted_env_` is active, at least four marker hits without encryption, successful sequential read of an empty file returning an empty slice, and `FSRandomAccessFile::GetFileSize()` returning `NotSupported` for encrypted random-access files.

The file is most useful when run in both encrypted and non-encrypted fixture configurations. The non-encrypted branch validates the detector, while the encrypted branch validates that the environment wrapper actually transforms stored file contents.
