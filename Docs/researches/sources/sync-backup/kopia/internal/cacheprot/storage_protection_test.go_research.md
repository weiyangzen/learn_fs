# sources/sync-backup/kopia/internal/cacheprot/storage_protection_test.go

Purpose: verifies the three `StorageProtection` implementations reset output buffers, round-trip payloads, and detect corruption where expected.

Important APIs/types/functions: `TestNoStorageProtection`, `TestHMACStorageProtection`, `TestEncryptionStorageProtection`, and shared helper `testStorageProtection`.

Control flow: each test protects a fixed payload into a buffer preloaded with dummy bytes, verifies into another preloaded buffer, compares unprotected bytes, flips the first protected byte, and asserts verification behavior based on whether the implementation should protect against bit flips.

State and persistence behavior: tests are in-memory only. They assert buffer reset semantics that matter to callers reusing `gather.WriteBuffer`.

Dependencies/integration: uses `cacheprot`, `gather`, `bytes`, and `testify/require`.

Risks/test signals: coverage is compact but important. It does not validate overhead values, id binding for authenticated encryption, wrong-key failures, or behavior with empty/large payloads.
