<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/StreamCipher.cpp -->
# sources/storage-engines/foundationdb/flow/StreamCipher.cpp
- Purpose: Implements Flow stream encryption/decryption and HMAC helpers around OpenSSL contexts, plus randomized round-trip tests.
- Important APIs/types/functions: `StreamCipherKey`, `StreamCipher`, `EncryptionStreamCipher`, `DecryptionStreamCipher`, `HmacSha256StreamCipher`, global key helpers, `cleanup`, and `TEST_CASE("flow/StreamCipher")`.
- Control flow: Global-key access lazily allocates a 256-bit key and registers it by UID. Encryption/decryption constructors initialize AES-256-GCM contexts with key and IV. `encrypt`, `decrypt`, and `finish` allocate output in an `Arena` and call OpenSSL update/final APIs. HMAC initializes SHA-256 and returns the final digest.
- State and persistence behavior: Static maps track active cipher contexts and keys for cleanup. Keys live in heap arrays and are zeroed by `reset()` through `StreamCipherKey::cleanup()`/destruction paths. Ciphertext is arena-allocated and not persisted by this file.
- Dependencies and integration points: Depends on OpenSSL EVP/HMAC APIs, Flow `Arena`, deterministic randomness, tracing, and unit-test registration. It is used by encryption-at-rest or network/storage serialization paths that need streaming crypto.
- Risks: AES-GCM authentication tag handling is not visible in this implementation, so callers must understand integrity guarantees. Static maps are not synchronized. `StreamCipher::cleanup()` frees contexts still owned by objects if called while instances live, so shutdown ordering matters.
- Test signals: The embedded test initializes a random global key, encrypts random plaintext in chunks, decrypts in chunks, and asserts exact equality. Additional coverage should include empty plaintext, HMAC updates from callers, and cleanup ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/StreamCipher.cpp -->
