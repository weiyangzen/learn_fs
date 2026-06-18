# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_crypto.py

## Purpose
This module tests Tahoe-LAFS cryptographic compatibility and validation wrappers for AES, Ed25519, RSA, and small crypto utilities. A major theme is preserving compatibility with old `pycryptopp` serialized keys, signatures, and AES stream behavior after migration to `cryptography`.

## Important APIs, types, and functions
- `TestRegression` loads legacy key and signature fixtures from `test/data` and exercises `aes.create_encryptor`, `aes.create_decryptor`, `aes.encrypt_data`, `aes.decrypt_data`, `ed25519.signing_keypair_from_string`, `ed25519.verifying_key_from_string`, `ed25519.sign_data`, `ed25519.verify_signature`, and `rsa.create_signing_keypair_from_string`.
- `TestEd25519` covers key generation, serialization/deserialization, signing, verification, and type validation.
- `TestRsa` covers RSA key generation, DER serialization, deserialization, signing, verification, bad signatures, and key-object validation.
- `TestUtil` covers `remove_prefix` and `BadPrefixError`.

## Control flow
Class-level fixture loading reads base64-encoded RSA data once from `RESOURCE_DIR`. The AES regression tests compare ciphertext bytes from known inputs with and without IV, including chunked processing that must match one-shot processing. Ed25519 regression reconstructs old private/public strings, compares derived and explicit public keys, checks deterministic legacy signature compatibility, and verifies both old and new signatures. RSA regression accepts a 2048-bit legacy private key and rejects legacy 1024-bit and 32768-bit keys. Later tests generate fresh keys and check round-trip serialization plus negative input validation.

## State and persistence behavior
The module itself has no persistent application state beyond fixture files. The important serialized state is cryptographic material: legacy pycryptopp RSA private/public bytes, signatures, Ed25519 string encodings, DER-encoded RSA keys, AES keys, and IVs. Tests assert byte-for-byte compatibility for serialized keys and encrypted/signature outputs where compatibility is required.

## Dependencies and integration points
Dependencies include `base64`, `binascii`, Twisted `FilePath`, Tahoe crypto modules, and Tahoe crypto error types. Integration is focused on Tahoe's compatibility surface: code that reads existing caps, mutable keys, or migrated nodes depends on these wrappers accepting old formats while rejecting insecure or malformed data.

## Risks
Cryptographic compatibility tests are intentionally byte-exact; changing cipher mode, counter initialization, key prefix parsing, serialization prefix, or RSA size policy can break stored data compatibility. Some negative tests assert exception message substrings, so error text changes can cause failures even when exception types remain correct. `TestRsa.test_sign_invalid_pubkey` creates a 1024-bit key even though legacy deserialization rejects tiny keys, so generated-key policy changes may require test updates.

## Test signals
Strong signals include Niels Ferguson AES known-answer vectors, short and long AES process compatibility, old Ed25519 and RSA fixture verification, key-size rejection boundaries, type checks for bytes-only data, invalid key-object checks, RSA bad-signature failure, and prefix-removal edge cases including empty, whole-string, bad, and partial prefixes.
