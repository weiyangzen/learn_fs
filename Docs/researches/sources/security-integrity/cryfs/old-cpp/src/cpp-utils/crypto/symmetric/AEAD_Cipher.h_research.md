# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/AEAD_Cipher.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 91 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CryptoPPCipher`, `AEADCipher`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_AEADCIPHER_H_`. Important declarations or call sites include `static constexpr unsigned int ciphertextSize(unsigned int plaintextBlockSize) {`; `static constexpr unsigned int plaintextSize(unsigned int ciphertextBlockSize) {`; `static Data encrypt(const CryptoPP::byte *plaintext, unsigned int plaintextSize, const EncryptionKey &encKey);`; `static boost::optional<Data> decrypt(const CryptoPP::byte *ciphertext, unsigned int ciphertextSize, const EncryptionKey &encKey);`; `Data AEADCipher<CryptoPPCipher, KEYSIZE_, IV_SIZE_, TAG_SIZE_>::encrypt(const CryptoPP::byte *plaintext, unsigned int plaintext...`; `ASSERT(encKey.binaryLength() == AEADCipher::KEYSIZE, "Wrong key size");`; `FixedSizeData<IV_SIZE> iv = Random::PseudoRandom().getFixedSize<IV_SIZE>();`; `encryption.SetKeyWithIV(static_cast<const CryptoPP::byte*>(encKey.data()), encKey.binaryLength(), iv.data(), IV_SIZE);`; `Data ciphertext(ciphertextSize(plaintextSize));`; `iv.ToBinary(ciphertext.data());`. CMake commands used here include `ASSERT`, `if`. Primary includes/dependencies visible in the file include `../../data/FixedSizeData.h`, `../../data/Data.h`, `../../random/Random.h`, `Cipher.h`, `EncryptionKey.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../../data/FixedSizeData.h`, `../../data/Data.h`, `../../random/Random.h`, `Cipher.h`, `EncryptionKey.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

## File-Specific Notes
- The AEAD adapter prefixes the randomly generated IV and appends Crypto++ authentication data, so ciphertext length is plaintext plus IV plus tag.
