# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite.hh

## Purpose

`XrdCryptoLite.hh` declares a minimal stream-crypto abstraction for simple encryption algorithms with built-in decryption validation. It is intentionally lighter than the full plugin-based `XrdCryptoBasic` hierarchy.

## Important APIs and Types

`Create()` constructs named algorithms and associates an arbitrary type byte. Pure virtual `Encrypt()` and `Decrypt()` operate on caller buffers. `Overhead()` returns the extra output bytes required by the concrete algorithm and `Type()` returns the assigned type code. Protected fields store `Extra` and `myType`.

## Control Flow

Consumers select an algorithm by string, allocate destination buffers using `Overhead()`, and call raw encrypt/decrypt with keys and lengths.

## State and Persistence Behavior

Instances persist only overhead and type metadata in the base class; concrete implementations hold no required base-managed cryptographic state.

## Dependencies and Integration Points

The header has no external includes. `XrdCryptoLite` is built as a shared library linked with OpenSSL for the `bf32` implementation.

## Risks and Edge Cases

The interface uses raw pointers and signed lengths, so callers must enforce `srcLen`, `dstLen`, and key validity. The comments contain a likely typo in the encrypt requirement (`srclen <= dstlen + Overhead()` should conceptually ensure destination is large enough for source plus overhead).

## Test Signals

Tests should verify buffer-size contracts, overhead reporting, and validation failure on corrupted ciphertext for each algorithm.
