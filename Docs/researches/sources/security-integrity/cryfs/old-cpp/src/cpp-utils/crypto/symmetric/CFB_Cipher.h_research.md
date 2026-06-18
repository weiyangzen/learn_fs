# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/CFB_Cipher.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 79 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CFB_Cipher`, `BlockCipher`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_CFBCIPHER_H_`. Important declarations or call sites include `static constexpr unsigned int ciphertextSize(unsigned int plaintextBlockSize) {`; `static constexpr unsigned int plaintextSize(unsigned int ciphertextBlockSize) {`; `static Data encrypt(const CryptoPP::byte *plaintext, unsigned int plaintextSize, const EncryptionKey &encKey);`; `static boost::optional<Data> decrypt(const CryptoPP::byte *ciphertext, unsigned int ciphertextSize, const EncryptionKey &encKey);`; `Data CFB_Cipher<BlockCipher, KeySize>::encrypt(const CryptoPP::byte *plaintext, unsigned int plaintextSize, const EncryptionKey...`; `ASSERT(encKey.binaryLength() == KeySize, "Wrong key size");`; `FixedSizeData<IV_SIZE> iv = Random::PseudoRandom().getFixedSize<IV_SIZE>();`; `auto encryption = typename CryptoPP::CFB_Mode<BlockCipher>::Encryption(static_cast<const CryptoPP::byte*>(encKey.data()), encKe...`; `Data ciphertext(ciphertextSize(plaintextSize));`; `iv.ToBinary(ciphertext.data());`. CMake commands used here include `ASSERT`, `if`. Primary includes/dependencies visible in the file include `../../data/FixedSizeData.h`, `../../data/Data.h`, `../../random/Random.h`, `boost/optional.hpp`, `vendor_cryptopp/modes.h`, `Cipher.h`, `EncryptionKey.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../../data/FixedSizeData.h`, `../../data/Data.h`, `../../random/Random.h`, `boost/optional.hpp`, `vendor_cryptopp/modes.h`, `Cipher.h`, `EncryptionKey.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

## File-Specific Notes
- The CFB adapter prefixes an IV but does not authenticate ciphertext; the source even carries a TODO around decrypt byte counts, making regression tests important.
