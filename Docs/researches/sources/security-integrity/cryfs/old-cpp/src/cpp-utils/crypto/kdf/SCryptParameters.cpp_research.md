# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/SCryptParameters.cpp

## Purpose
Provides the password-based key derivation abstraction and the scrypt implementation/parameter serialization used to derive encryption keys from user passwords. This specific file has 41 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `Data SCryptParameters::serialize() const {`; `Serializer serializer(_serializedSize());`; `serializer.writeUint64(_n);`; `serializer.writeUint32(_r);`; `serializer.writeUint32(_p);`; `serializer.writeTailData(_salt);`; `return serializer.finished();`; `size_t SCryptParameters::_serializedSize() const {`; `return _salt.size() + sizeof(uint64_t) + sizeof(uint32_t) + sizeof(uint32_t);`; `SCryptParameters SCryptParameters::deserialize(const cpputils::Data &data) {`. Primary includes/dependencies visible in the file include `SCryptParameters.h`.

## Control Flow
Existing-key derivation deserializes saved KDF parameters, derives a key with Crypto++ scrypt, and verifies the parameters were fully consumed. New-key derivation creates salt/settings first and returns both the key and serialized parameters.

## State and Persistence Behavior
KDF parameters persist as serialized `Data` containing N/r/p and salt. Derived keys are in unswappable `EncryptionKey` buffers, while settings for new keys live in the `SCrypt` instance.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `SCryptParameters.h`.

## Risks and Edge Cases
Scrypt parameter compatibility is critical for existing vaults. Weak N/r/p settings or salt reuse reduce password-hardening strength, and deserialization must reject truncated parameter blobs.

## Test Signals
Round-trip serialized scrypt parameters, derive stable existing keys from fixtures, reject malformed parameter data, and verify new-key salt uniqueness.

## File-Specific Notes
- Serialization order is `uint64 n`, `uint32 r`, `uint32 p`, followed by tail salt; existing vault compatibility depends on this exact format.
