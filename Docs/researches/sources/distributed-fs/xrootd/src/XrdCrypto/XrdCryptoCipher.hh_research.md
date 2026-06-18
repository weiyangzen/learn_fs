# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoCipher.hh

## Purpose

`XrdCryptoCipher.hh` declares the abstract interface for symmetric ciphers and key-agreement ciphers in the plugin crypto architecture.

## Important APIs and Types

The interface exposes key-agreement finalization, validity checks, output sizing, bucket serialization, IV getters/setters, public key material, encryption/decryption on raw buffers and `XrdSutBucket`, and IV refresh. It inherits buffer/type behavior from `XrdCryptoBasic`.

## Control Flow

Concrete plugin classes override the virtual methods. Consumers can use either raw buffer APIs or bucket wrappers that handle IV packing.

## State and Persistence Behavior

The abstract class itself persists only inherited buffer state. Concrete implementations own cryptographic context and IV/key state.

## Dependencies and Integration Points

It depends on `XrdSutBucket` and `XrdCryptoBasic`. `XrdCryptoFactory` constructs instances and authentication/protocol code uses them for encrypted buckets.

## Risks and Edge Cases

The API mixes raw pointer ownership, mutable IV state, and signed lengths. Implementations must document whether returned `IV()`/`Public()` buffers are borrowed or owned.

## Test Signals

Interface conformance tests should verify concrete ciphers support both raw and bucket modes, padding behavior, and default length reporting.
