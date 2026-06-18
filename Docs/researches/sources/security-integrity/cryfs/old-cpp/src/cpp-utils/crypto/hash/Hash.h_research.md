# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash/Hash.h

## Purpose
Provides salted SHA-512 hashing helpers over cpp-utils `Data` buffers and fixed-size salt/digest value types. This specific file has 29 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Hash`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_HASH_HASH_H`. Important declarations or call sites include `Salt generateSalt();`; `Hash hash(const cpputils::Data& data, Salt salt);`. Primary includes/dependencies visible in the file include `cpp-utils/data/FixedSizeData.h`, `cpp-utils/data/Data.h`.

## Control Flow
Hashing initializes a Crypto++ SHA-512 instance, feeds salt before data, finalizes into a fixed-size digest, and returns value objects rather than mutable buffers.

## State and Persistence Behavior
No state is persisted by the helper; salt and digest bytes are caller-owned fixed-size values.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `cpp-utils/data/FixedSizeData.h`, `cpp-utils/data/Data.h`.

## Risks and Edge Cases
Salt must be unique and stored with the digest by callers. Hash comparison is not constant-time here, so authentication decisions should use higher-level crypto where needed.

## Test Signals
Known-vector tests should verify salt+data order, digest size, null/empty data handling, and salt generation length.
