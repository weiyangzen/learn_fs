# sources/storage-engines/badger/key_registry_test.go

## Purpose
`key_registry_test.go` validates Badger encryption key registry creation, persistence, rewrite, mismatch detection, decryption, and in-memory mode.

## Important APIs, Types, and Functions
- `getRegistryTestOptions`: helper for `KeyRegistryOptions`.
- `TestBuildRegistry`: creates two rotated keys, closes, reopens, and checks both keys are present.
- `TestRewriteRegistry`: creates keys, deletes one from memory, calls `WriteKeyRegistry`, and verifies the rewritten file has one key.
- `TestMismatch`: verifies opening with a different storage key returns `ErrEncryptionKeyMismatch`.
- `TestEncryptionAndDecryption`: checks a generated data key round-trips through disk.
- `TestKeyRegistryInMemory`: verifies in-memory registry can generate multiple keys without disk paths.

## Control Flow and State
Tests generate 32-byte random storage keys, use temp directories, call `OpenKeyRegistry`, force rotation by setting `lastCreated = 0`, and close/reopen as needed. The rewrite test mutates the in-memory map to simulate compaction of registry contents.

## Persistence Behavior
Disk tests verify `KEYREGISTRY` contents survive close/reopen, can be atomically rewritten, and cannot be opened with the wrong storage key. In-memory mode intentionally avoids disk persistence.

## Dependencies and Integration Points
Depends on `crypto/math rand` style random bytes from `math/rand` in this file, `os.MkdirTemp`, `testify/require`, and registry APIs.

## Risks and Edge Cases
Tests do not cover invalid encryption-key lengths, checksum corruption, partial records, concurrent `LatestDataKey`, or read-only registry behavior. The random source is `math/rand`, which is adequate for tests but not representative of production key generation.

## Test Signals
Focused coverage for key-registry persistence and encryption-key validation. Complements DB-level encryption tests in `db_test.go` and `db2_test.go`.
