# sources/object-store/minio/cmd/config-encrypted_test.go

## Purpose
`config-encrypted_test.go` verifies madmin encrypted config payload round-tripping with MinIO credentials.

## Important APIs, Types, And Functions
`TestDecryptData` builds two `auth.Credentials`, encrypts `config data` with `madmin.EncryptData`, and decrypts with `madmin.DecryptData`.

## Control Flow
The test table covers two encrypted payloads with matching credentials and one plaintext payload expected to fail decryption. Successful decryptions are byte-compared to the original data.

## State And Persistence Behavior
No persistent state is written. All encryption/decryption work is in memory.

## Dependencies And Integration Points
The test targets the same madmin encryption primitives used historically by config migration/decryption paths. It depends on `auth.Credentials.String()` as the encryption key material.

## Risks And Test Signals
This test does not directly call MinIO's `decryptData` wrapper or KMS-backed encryption. It is a focused compatibility signal that credential-derived encrypted blobs can still be read and plaintext is rejected by `madmin.DecryptData`.
