# sources/storage-engines/foundationdb/flow/include/flow/EncryptUtils.h

## Purpose
`EncryptUtils.h` centralizes Flow encryption domain IDs, cipher IDs, encryption modes, header authentication modes/algorithms, token sizes, and debug trace-key helpers.

## Important APIs, Types, And Functions
Important aliases include `EncryptCipherDomainId`, `EncryptCipherBaseKeyId`, `EncryptCipherRandomSalt`, and `EncryptCipherKeyCheckValue`. It defines reserved/default domain constants, `EncryptCipherMode`, `EncryptAuthTokenMode`, `EncryptAuthTokenAlgo`, validation helpers, random mode/algo helpers, debug trace key builders, `getEncryptHeaderAuthTokenSize()`, `isReservedEncryptDomain()`, and `isEncryptHeaderDomain()`.

## Control Flow
Most behavior is implemented out of line. Callers parse modes, validate mode/algo combinations, choose random authentication settings for testing, build trace keys with optional base cipher IDs and timestamps, and map auth algorithms to token sizes.

## State And Persistence Behavior
The header declares constants and static unordered sets for system/default domains. It does not persist key material. Domain and base-key IDs are persisted by callers in encryption metadata and trace strings.

## Dependencies And Integration Points
It depends on `Arena`, `xxhash`, OpenSSL `EVP_MAX_KEY_LENGTH`, `Optional`, strings, and unordered sets. It integrates with blob cipher/header code, encryption key cache knobs, and tracing.

## Risks And Edge Cases
Reserved negative domains must not collide with user domains. `MAX_BASE_CIPHER_LEN` depends on OpenSSL limits and salt size. Auth token mode/algo mismatches can silently weaken header integrity if validation is skipped. Static set name typo `DETAULT` is API surface if referenced.

## Test Signals
Tests should cover mode parsing, valid/invalid auth combinations, token sizes for HMAC and CMAC, reserved domain checks, random helper bounds, trace key formatting, and compile-time enum-size asserts.
