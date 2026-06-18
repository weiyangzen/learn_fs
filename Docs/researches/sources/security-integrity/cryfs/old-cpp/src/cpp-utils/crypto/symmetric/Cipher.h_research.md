# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/Cipher.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 36 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `X`, `CipherConcept`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_CIPHER_H_`. Important declarations or call sites include `BOOST_CONCEPT_USAGE(CipherConcept) {`; `same_type(UINT32_C(0), X::ciphertextSize(UINT32_C(5)));`; `same_type(UINT32_C(0), X::plaintextSize(UINT32_C(5)));`; `same_type(UINT32_C(0), X::KEYSIZE);`; `same_type(UINT32_C(0), X::STRING_KEYSIZE);`; `typename X::EncryptionKey key = X::EncryptionKey::CreateKey(Random::OSRandom(), X::KEYSIZE);`; `same_type(Data(0), X::encrypt(static_cast<uint8_t*>(nullptr), UINT32_C(0), key));`; `same_type(boost::optional<Data>(Data(0)), X::decrypt(static_cast<uint8_t*>(nullptr), UINT32_C(0), key));`; `template <typename T> void same_type(T const&, T const&);`. CMake commands used here include `BOOST_CONCEPT_USAGE`, `same_type`. Primary includes/dependencies visible in the file include `boost/concept_check.hpp`, `cstdint`, `../../data/Data.h`, `../../random/Random.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `boost/concept_check.hpp`, `cstdint`, `../../data/Data.h`, `../../random/Random.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.
