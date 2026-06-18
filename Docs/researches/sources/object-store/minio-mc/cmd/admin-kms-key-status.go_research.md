# sources/object-store/minio-mc/cmd/admin-kms-key-status.go

## Purpose
Implements `mc admin kms key status`, checking encryption and decryption availability for the default or named KMS key.

## Important APIs, types, and functions
`adminKMSKeyStatusCmd` defines command metadata. `mainAdminKMSKeyStatus` calls `GetKeyStatus`. `kmsKeyStatusMsg` renders key ID, encryption error, decryption error, and success status.

## Control flow
The command accepts target plus optional key name. It creates an admin client, requests key status, and prints a two-line capability view. If encryption failed, decryption status is shown as unknown because decryption cannot be meaningfully inferred.

## State and persistence behavior
No state is changed. The command reads runtime KMS connectivity and capability state from the server.

## Dependencies and integration points
It integrates `madmin-go` KMS status APIs, global output mode, `colorjson`, console color themes, and `probe` error handling.

## Risks and edge cases
An encryption failure masks decryption as unknown in human output even if a decryption error string is present. The default-key path uses an empty key ID, relying on server semantics.

## Test signals
Tests should cover target-only default key status, named key status, encryption success/failure, decryption failure, JSON status mutation to `success`, and invalid arity rejection.
