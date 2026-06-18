# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/ciphers.cpp

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 36 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `DEFINE_CIPHER`. Important declarations or call sites include `DEFINE_CIPHER(XChaCha20Poly1305);`; `DEFINE_CIPHER(AES256_GCM);`; `DEFINE_CIPHER(AES256_CFB);`; `DEFINE_CIPHER(AES128_GCM);`; `DEFINE_CIPHER(AES128_CFB);`; `DEFINE_CIPHER(Twofish256_GCM);`; `DEFINE_CIPHER(Twofish256_CFB);`; `DEFINE_CIPHER(Twofish128_GCM);`; `DEFINE_CIPHER(Twofish128_CFB);`; `DEFINE_CIPHER(Serpent256_GCM);`. CMake commands used here include `DEFINE_CIPHER`. Primary includes/dependencies visible in the file include `ciphers.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `ciphers.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.
