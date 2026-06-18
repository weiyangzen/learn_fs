# sources/security-integrity/fscrypt/crypto/crypto_test.go

## Purpose
Comprehensive tests and benchmarks for key construction, memory locking toggles, randomness smoke checks, key wrapping/unwrapping, descriptors, and Argon2 passphrase hashing.

## APIs and Control Flow
Defines `ConstReader`, fixed fake keys, passphrase hash test vectors, and helpers for length checks, compression checks, distinct-buffer checks, and wrap/unwrap equality. Tests cover reader-based keys, wiping, invalid/zero lengths, mlock toggles, resizing, random key generation, large key allocation with `ErrMlockUlimit` tolerance, distinct derived outputs, wrap data lengths, fixed and random wrap/unwrap, variable secret lengths, wrong wrapping key lengths, randomized IVs, authentication failure on key/ciphertext/IV/HMAC modification, v1/v2 descriptor vectors, bad descriptor version, Argon2 vectors, and invalid hashing costs. Benchmarks cover wrap, unwrap with and without mlock, random wrap/unwrap, and passphrase hashing at several cost profiles.

## State, Dependencies, and Integration
Tests use real `Key` memory behavior, random generation, AES/HMAC/HKDF/Argon2 implementations, and metadata constants. Some tests toggle global `UseMlock`.

## Risks and Test Signals
The test vectors are strong regression signals for crypto compatibility. Randomness compression is only a smoke test. Global `UseMlock` toggles must be restored to avoid cross-test contamination.
