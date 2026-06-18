# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/EncryptionKey.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 107 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `EncryptionKey`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_ENCRYPTIONKEY_H_`. Important declarations or call sites include `: _keyData(std::move(keyData)) {`; `size_t binaryLength() const {`; `return _keyData->size();`; `size_t stringLength() const {`; `return 2 * binaryLength();`; `static EncryptionKey Null(size_t keySize) {`; `data->FillWithZeroes();`; `return EncryptionKey(std::move(data));`; `static EncryptionKey FromString(const std::string& keyData) {`; `EncryptionKey key(std::move(data));`. CMake commands used here include `EncryptionKey`, `ASSERT`. Primary includes/dependencies visible in the file include `cpp-utils/data/FixedSizeData.h`, `memory`, `cpp-utils/system/memory.h`, `cpp-utils/random/RandomGenerator.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `cpp-utils/data/FixedSizeData.h`, `memory`, `cpp-utils/system/memory.h`, `cpp-utils/random/RandomGenerator.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

## File-Specific Notes
- `EncryptionKey` stores key bytes in `Data` allocated through `UnswappableAllocator` and shares that memory through `shared_ptr` to avoid casual copies.
