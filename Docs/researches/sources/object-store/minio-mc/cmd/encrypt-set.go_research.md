# sources/object-store/minio-mc/cmd/encrypt-set.go

Purpose: Implements `mc encrypt set` to enable bucket auto-encryption.

Important APIs/types/functions: `encryptSetCmd`, `checkEncryptSetSyntax`, `encryptSetMessage`, and `mainEncryptSet`.

Control flow: Accepts either `sse-s3 TARGET` or `sse-kms KEY TARGET`, lowercases the algorithm, validates it is `sse-s3` or `sse-kms`, creates a client, calls `SetEncryption`, and prints success.

State and persistence: Mutates remote bucket encryption configuration.

Dependencies/integration: Uses global context, `newClient`, client encryption API, probe errors, and console/json output.

Risks: Does not require a key ID for `sse-kms` in this file despite examples implying one. Does not reject a key ID for `sse-s3` if three args are supplied.

Test signals: No direct tests.
