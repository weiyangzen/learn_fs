# sources/object-store/minio-mc/cmd/encryption-methods_test.go

Purpose: Unit tests for encryption key string parsing.

Important APIs/types/functions: `TestParseEncryptionKeys`.

Control flow: A table feeds `parseSSEKey` with SSE-C, KMS, and S3 formats. Success cases assert alias/prefix/object reconstruction and decoded plaintext key. Failure cases cover invalid base64/hex, wrong lengths, spaces/symbols, and invalid KMS names.

State and persistence: No state or I/O.

Dependencies/integration: Uses Go `testing` and `fmt`.

Risks: Does not test `validateAndCreateEncryptionKeys`, alias existence, prefix overlap, sorting, or CLI argument matching.

Test signals: Strong focused coverage for the parser's last-`=` split behavior and 32-byte SSE-C key requirement.
