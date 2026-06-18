# sources/storage-engines/lmdb/libraries/liblmdb/crypto.c

## Purpose
Implements a dynamically loadable LMDB crypto helper module backed by libsodium. It exposes the `MDB_crypto` hook expected by LMDB command-line tools for encrypted/checksummed environments.

## Important APIs, Types, And Functions
Global `MDB_crypto_hooks MDB_crypto;` declares the exported hook symbol type. `mcf_str2key` derives a key by hashing a constant string plus the passphrase with SHA-256. `mcf_encfunc` encrypts or decrypts page data using `crypto_aead_chacha20poly1305_ietf_*` and, for unauthenticated header loads, falls back to `crypto_stream_chacha20_ietf_xor_ic`. `mcf_table` advertises key size, MAC size, and no plain checksum. `MDB_crypto()` returns the table.

## Control Flow
`mcf_encfunc` builds a 12-byte nonce from the second key slot, using low 32 bits plus an `mdb_size_t` value. If `encdec` is true it encrypts and writes the MAC to `key[2]`; otherwise it checks whether MAC storage is present and either authenticated-decrypts or performs unauthenticated stream decryption for incremental-load page headers.

## State And Persistence Behavior
The module keeps a static function table but no mutable persistent state. Key material and MAC buffers are supplied through `MDB_val` arrays by the caller. Encrypted output is written to caller-provided destination buffers.

## Dependencies And Integration Points
It depends on libsodium and `lmdb.h` crypto hook types. The makefile builds it as `crypto.lm` with `-shared` and `-lsodium`, and LMDB tools can load it through `mdb_modload`/`mdb_modsetup`.

## Risks And Edge Cases
The KDF is a single SHA-256 pass over a constant and passphrase, with no salt or work factor. The nonce construction must be unique for a key; reuse would compromise stream/AEAD security. The unauthenticated decrypt path is explicitly for incremental-load headers and should not be generalized.

## Test Signals
Build success requires libsodium headers and library. Encryption-related mtest/tool flows are the functional signal for hook loading, key derivation, encryption, MAC verification, and header fallback.
