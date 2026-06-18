# sources/object-store/openstack-swift/swift/common/middleware/crypto/crypto_utils.py

## Purpose
`crypto_utils.py` provides shared primitives for Swift encryption middleware: AES-CTR encryption/decryption, random IV/key generation, simple key wrapping, crypto metadata validation/serialization, and WSGI context helpers for retrieving keys from keymaster callbacks.

## Important APIs, Types, and Functions
`CRYPTO_KEY_CALLBACK` names the environ key `swift.callback.fetch_crypto_keys`. `Crypto` exposes `create_encryption_ctxt()`, `create_decryption_ctxt()`, `create_iv()`, `create_crypto_meta()`, `check_crypto_meta()`, `create_random_key()`, `wrap_key()`, `unwrap_key()`, and `check_key()`. `CryptoWSGIContext` adds `get_keys()` and `get_multiple_keys()`. Utility functions include `dump_crypto_meta()`, `load_crypto_meta()`, `append_crypto_meta()`, and `extract_crypto_meta()`.

## Control Flow
`Crypto` memoizes the cryptography backend and uses AES-CTR with 256-bit keys and block-sized IVs. Decryption supports range offsets by incrementing the CTR IV by block offset and discarding bytes inside the first block. Metadata serialization JSON-encodes nested dicts, base64-encodes `iv` and `key` fields, sorts keys for deterministic output, and URL-quotes the JSON. Metadata extraction uses Swift header parsing to find `swift_meta`.

## State and Persistence
Process-local state is limited to the logger and crypto backend. Persistent state is serialized crypto metadata stored by encrypter in headers/sysmeta and later parsed by decrypter. No keys are stored by this module.

## Dependencies and Integration Points
It depends on `cryptography`, Swift exceptions, `HTTPInternalServerError`, `parse_header`, and `WSGIContext`. `CryptoWSGIContext` is the common integration point between encrypter/decrypter and keymaster middleware.

## Risks and Edge Cases
Missing key callbacks or malformed returned key dicts are converted to 500s. Unknown secret ids propagate for callers that can decide whether to mask listing entries or fail object decrypts. Metadata parsing must reject non-string, non-dict, bad JSON, and bad base64 inputs. AES-CTR does not authenticate ciphertext; integrity is handled separately through ETags/HMACs and storage behavior.

## Test Signals
Tests should cover key-length validation, IV length/cipher validation, offset decryption equivalence, key wrapping/unwrapping, metadata round trips with nested key/iv values, malformed metadata errors, callback missing/failing behavior, required-key validation, multiple-key retrieval across all ids, and URL/base64 encoding compatibility.
