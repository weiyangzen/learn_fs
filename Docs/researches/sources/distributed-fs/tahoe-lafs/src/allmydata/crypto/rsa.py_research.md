# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/rsa.py

## Purpose

This module wraps RSA signing-key creation, DER serialization/deserialization, signing, and verification behind Tahoe-local helper functions.

## Important APIs, Types, And Functions

`PublicKey` and `PrivateKey` are type aliases for cryptography RSA key types. `RSA_PSS_SALT_LENGTH` is fixed at 32 for pycryptopp compatibility. `RSA_PADDING` is PSS with MGF1/SHA-256 and the fixed salt length. `create_signing_keypair()` generates a new key. `create_signing_keypair_from_string()` loads DER private keys with careful validation. `der_string_from_signing_key()` and `der_string_from_verifying_key()` serialize private/public keys. `create_verifying_key_from_string()` loads a public DER key. `sign_data()` and `verify_signature()` perform PSS/SHA-256 signatures, raising `BadSignature` for invalid signatures. Validation helpers enforce RSA key object types.

## Control Flow

Key loading first attempts an unsafe-skip-validation load when supported, checks that the object is an RSA private key and exactly 2048 bits, then reloads with OpenSSL validation. This balances protection from expensive malformed-key validation with final safety. Signing and verification validate key types and delegate to cryptography.

## State And Persistence

The module has immutable padding constants. DER private/public keys are persisted by callers, especially mutable-file key material. No mutable module state exists.

## Dependencies And Integration Points

It depends on cryptography RSA, hashes, PSS padding, DER serializers/loaders, `typing_extensions.TypeAlias`, and Tahoe `BadSignature`. It integrates with mutable file/directory key generation and client `KeyGenerator`, which creates 2048-bit RSA pairs on a CPU thread.

## Risks

The fixed 2048-bit requirement is a compatibility/security policy; loading other key sizes raises. The unsafe initial load path depends on cryptography version support and must remain paired with later validation. PSS salt length must not be changed casually because old signatures depend on 32 bytes, not cryptography's max salt length. Serialization is unencrypted DER, so caller storage protections are critical.

## Test Signals

Generate 2048-bit keys, serialize/load DER, sign/verify success, reject tampered signatures and data, reject non-RSA/private/public object misuse, reject non-2048 private keys, and run tests under cryptography versions with and without `unsafe_skip_rsa_key_validation`.
