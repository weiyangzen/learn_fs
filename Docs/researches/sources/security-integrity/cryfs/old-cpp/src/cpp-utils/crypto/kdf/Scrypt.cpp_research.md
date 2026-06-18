# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/Scrypt.cpp

## Purpose
Provides the password-based key derivation abstraction and the scrypt implementation/parameter serialization used to derive encryption keys from user passwords. This specific file has 53 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `EncryptionKey _derive(size_t keySize, const std::string& password, const SCryptParameters& kdfParameters) {`; `auto result = EncryptionKey::Null(keySize);`; `if (status != 1) {`; `throw std::runtime_error("Error running scrypt key derivation. Error code: "+std::to_string(status));`; `SCryptParameters _createNewSCryptParameters(const SCryptSettings& settings) {`; `return SCryptParameters(Random::PseudoRandom().get(settings.SALT_LEN), settings.N, settings.r, settings.p);`; `:_settingsForNewKeys(settingsForNewKeys) {`; `EncryptionKey SCrypt::deriveExistingKey(size_t keySize, const std::string& password, const Data& kdfParameters) {`; `SCryptParameters parameters = SCryptParameters::deserialize(kdfParameters);`; `auto key = _derive(keySize, password, parameters);`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `Scrypt.h`, `vendor_cryptopp/scrypt.h`.

## Control Flow
Existing-key derivation deserializes saved KDF parameters, derives a key with Crypto++ scrypt, and verifies the parameters were fully consumed. New-key derivation creates salt/settings first and returns both the key and serialized parameters.

## State and Persistence Behavior
KDF parameters persist as serialized `Data` containing N/r/p and salt. Derived keys are in unswappable `EncryptionKey` buffers, while settings for new keys live in the `SCrypt` instance.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `Scrypt.h`, `vendor_cryptopp/scrypt.h`.

## Risks and Edge Cases
Scrypt parameter compatibility is critical for existing vaults. Weak N/r/p settings or salt reuse reduce password-hardening strength, and deserialization must reject truncated parameter blobs.

## Test Signals
Round-trip serialized scrypt parameters, derive stable existing keys from fixtures, reject malformed parameter data, and verify new-key salt uniqueness.

## File-Specific Notes
- The implementation throws when Crypto++ `DeriveKey` does not return success and asserts the derived key has the requested size.
