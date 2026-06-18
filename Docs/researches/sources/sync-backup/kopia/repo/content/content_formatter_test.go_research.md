# sources/sync-backup/kopia/repo/content/content_formatter_test.go

Purpose: end-to-end tests for content hashing, encryption, decryption, formatting, writing, flushing, and reading across all supported hash and encryption algorithms.

Important APIs/types/functions: `TestFormatters`, `verifyEndToEndFormatter`, and `mustCreateFormatProvider` use `hashing.SupportedAlgorithms`, `encryption.SupportedAlgorithms`, `NewManagerForTesting`, `WriteContent`, `GetContent`, and `Flush`.

Control flow: for each hash/encryption pair, the test computes a content ID, encrypts random data, decrypts it, and compares SHA-1 of plaintext. It then creates an in-memory content manager and writes several payload sizes/patterns without compression, reads each before and after `Flush`, and compares bytes.

State and persistence behavior: storage state is an in-memory `blobtesting.DataMap` with key timestamps. Format provider uses test HMAC secret, zero master key, mutable parameters, and selected algorithms.

Dependencies/integration: exercises hashing, encryption, format provider, content manager, blob map storage, gather buffers, and committed read/write paths.

Risks and edge cases: algorithm matrix can be expensive but gives broad compatibility coverage. The test focuses on no-compression content writes; compression-specific behavior is covered elsewhere.

Test signals: failures indicate broken hash/encryption setup, content ID derivation, encrypt/decrypt round-trip, content manager read/write before flush, or committed read after flush.
