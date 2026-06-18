# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/GCM_Cipher.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 16 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_GCMCIPHER_H_`. Primary includes/dependencies visible in the file include `AEAD_Cipher.h`, `vendor_cryptopp/gcm.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `AEAD_Cipher.h`, `vendor_cryptopp/gcm.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.
