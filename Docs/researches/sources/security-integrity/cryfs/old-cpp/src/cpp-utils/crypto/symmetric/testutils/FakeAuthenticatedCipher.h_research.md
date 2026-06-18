# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils/FakeAuthenticatedCipher.h

## Purpose
Provides a deterministic fake authenticated cipher for tests that need cipher-like behavior without relying on real cryptographic transformations. This specific file has 122 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `FakeKey`, `FakeAuthenticatedCipher`. Macros/constants: `MESSMER_CPPUTILS_TEST_CRYPTO_SYMMETRIC_TESTUTILS_FAKEAUTHENTICATEDCIPHER_H_`. Important declarations or call sites include `static FakeKey FromString(const std::string& keyData) {`; `size_t binaryLength() const {`; `return sizeof(uint64_t);`; `static FakeKey CreateKey(RandomGenerator &randomGenerator, size_t keySize) {`; `ASSERT(keySize == sizeof(uint64_t), "Wrong key size");`; `auto data = randomGenerator.getFixedSize<sizeof(uint64_t)>();`; `BOOST_CONCEPT_ASSERT((CipherConcept<FakeAuthenticatedCipher>));`; `static constexpr unsigned int KEYSIZE = sizeof(uint64_t);`; `static EncryptionKey Key1() {`; `static EncryptionKey Key2() {`. CMake commands used here include `ASSERT`, `BOOST_CONCEPT_ASSERT`, `_xor`, `if`, `for`. Primary includes/dependencies visible in the file include `cpp-utils/crypto/symmetric/Cipher.h`, `cpp-utils/data/FixedSizeData.h`, `cpp-utils/data/Data.h`, `cpp-utils/random/RandomGenerator.h`, `random`, `cpp-utils/data/SerializationHelper.h`.

## Control Flow
The fake cipher derives deterministic output from the fake key and payload sizes, appends/checks an authentication marker, and exposes the same static API shape as real ciphers for concept-based tests.

## State and Persistence Behavior
The fake cipher keeps no global state; deterministic fake keys and serialized test payloads are created in memory.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cpp-utils/crypto/symmetric/Cipher.h`, `cpp-utils/data/FixedSizeData.h`, `cpp-utils/data/Data.h`, `cpp-utils/random/RandomGenerator.h`, `random`, `cpp-utils/data/SerializationHelper.h`.

## Risks and Edge Cases
The fake cipher is intentionally not secure and must remain test-only. Accidentally linking it into production paths would invalidate crypto guarantees.

## Test Signals
Use it only in tests that verify authentication-failure plumbing, serialization sizes, and deterministic fake key behavior.
