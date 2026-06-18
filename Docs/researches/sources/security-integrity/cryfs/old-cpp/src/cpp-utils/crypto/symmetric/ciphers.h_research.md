# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/ciphers.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 64 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `InstanceName`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_CIPHERS_H_`, `SINGLE_ARG`, `DECLARE_CIPHER`. Important declarations or call sites include `BOOST_CONCEPT_ASSERT((CipherConcept<InstanceName>));                               \`; `DECLARE_CIPHER(XChaCha20Poly1305, "xchacha20-poly1305", SINGLE_ARG(AEADCipher<CryptoPP::XChaCha20Poly1305, 32, 24, 16>));`; `static_assert(32 == CryptoPP::AES::MAX_KEYLENGTH, "If AES offered larger keys, we should offer a variant with it");`; `DECLARE_CIPHER(AES256_GCM, "aes-256-gcm", SINGLE_ARG(GCM_Cipher<CryptoPP::AES, 32>));`; `DECLARE_CIPHER(AES256_CFB, "aes-256-cfb", SINGLE_ARG(CFB_Cipher<CryptoPP::AES, 32>));`; `DECLARE_CIPHER(AES128_GCM, "aes-128-gcm", SINGLE_ARG(GCM_Cipher<CryptoPP::AES, 16>));`; `DECLARE_CIPHER(AES128_CFB, "aes-128-cfb", SINGLE_ARG(CFB_Cipher<CryptoPP::AES, 16>));`; `static_assert(32 == CryptoPP::Twofish::MAX_KEYLENGTH, "If Twofish offered larger keys, we should offer a variant with it");`; `DECLARE_CIPHER(Twofish256_GCM, "twofish-256-gcm", SINGLE_ARG(GCM_Cipher<CryptoPP::Twofish, 32>));`; `DECLARE_CIPHER(Twofish256_CFB, "twofish-256-cfb", SINGLE_ARG(CFB_Cipher<CryptoPP::Twofish, 32>));`. CMake commands used here include `BOOST_CONCEPT_ASSERT`, `DECLARE_CIPHER`, `static_assert`. Primary includes/dependencies visible in the file include `vendor_cryptopp/aes.h`, `vendor_cryptopp/twofish.h`, `vendor_cryptopp/serpent.h`, `vendor_cryptopp/cast.h`, `vendor_cryptopp/mars.h`, `vendor_cryptopp/chachapoly.h`, `GCM_Cipher.h`, `CFB_Cipher.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `vendor_cryptopp/aes.h`, `vendor_cryptopp/twofish.h`, `vendor_cryptopp/serpent.h`, `vendor_cryptopp/cast.h`, `vendor_cryptopp/mars.h`, `vendor_cryptopp/chachapoly.h`, `GCM_Cipher.h`, `CFB_Cipher.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.
