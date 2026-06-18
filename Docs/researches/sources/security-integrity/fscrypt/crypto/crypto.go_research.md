# sources/security-integrity/fscrypt/crypto/crypto.go

## Purpose
Implements fscrypt cryptographic primitives: key wrapping/unwrapping, HMAC authentication, descriptor computation, and passphrase hashing.

## APIs, Types, and Control Flow
Exports `ErrBadAuth`, `ErrRecoveryCode`, `ErrMlockUlimit`, `Wrap`, `Unwrap`, `ComputeKeyDescriptor`, and `PassphraseHash`. Internal helpers validate lengths, stretch an internal key into encryption and authentication keys with HKDF-SHA256, run AES-256-CTR, and compute HMAC-SHA256.

`Wrap` validates a 32-byte wrapping key, allocates encrypted key data, generates random IV, stretches the wrapping key, encrypts the secret key with AES-CTR, and stores HMAC over IV and ciphertext. `Unwrap` repeats stretching, verifies HMAC with constant-time comparison, allocates a blank key, and decrypts. Descriptor v1 is first 8 bytes of double SHA-512; descriptor v2 is kernel-compatible HKDF-SHA512 with `fscrypt\0\x01` info. `PassphraseHash` runs Argon2id with configured time, memory, and parallelism and copies output into a locked key.

## State, Dependencies, and Integration
Crypto state is in-memory `Key` objects from `key.go`, with explicit wiping. Persistent wrapped data is represented by `metadata.WrappedKeyData`. Action-layer protectors and policies depend on these primitives for all key wrapping and descriptors.

## Risks and Test Signals
Length validation panics in low-level helpers but public wrapping returns errors for bad wrapping keys. HKDF is unsalted by design for key splitting and descriptor compatibility. `PassphraseHash` assumes costs were validated elsewhere. Tests cover key creation/wiping, wrapping integrity, descriptor vectors, passphrase vectors, invalid costs, and benchmarks.
