# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/aes.py

## Purpose

This module provides Tahoe-local AES-CTR encryptor/decryptor helpers around the `cryptography` library.

## Important APIs, Types, And Functions

`DEFAULT_IV` is sixteen zero bytes. `Encryptor` and `Decryptor` dataclasses wrap `CipherContext` objects. `create_encryptor()` and `create_decryptor()` validate key/IV and create AES-CTR contexts. `encrypt_data()` and `decrypt_data()` call `update()` after validating bytes-like input. `_validate_key()` allows 16- or 32-byte keys, and `_validate_iv()` allows `None` or a 16-byte IV.

## Control Flow

Callers create a context, then stream data through `encrypt_data()` or `decrypt_data()`. `_create_cryptor()` always creates an encryptor context over AES-CTR because CTR encryption and decryption are the same keystream operation; the wrapper names separate caller intent.

## State And Persistence

The only state is cryptography cipher context state inside wrapper dataclasses. Contexts are not persisted and should not be reused across unrelated streams.

## Dependencies And Integration Points

It depends on `cryptography.hazmat` ciphers and is used by directory-node writecap encryption and other Tahoe crypto paths that require AES-CTR.

## Risks

The default all-zero IV is safe only when the caller's keying construction guarantees unique keystreams for its context; careless reuse with the same key would be catastrophic in CTR mode. `decrypt_data()` names its second parameter `plaintext`, a misleading label for ciphertext input. The functions do not finalize contexts, which is acceptable for CTR but should remain intentional.

## Test Signals

Round-trip 16- and 32-byte keys, explicit and default IVs, memoryview input, invalid key/IV types and lengths, and known AES-CTR vectors. Tests should also ensure context reuse behavior is understood.
