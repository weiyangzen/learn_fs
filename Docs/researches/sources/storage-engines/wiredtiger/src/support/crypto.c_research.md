# sources/storage-engines/wiredtiger/src/support/crypto.c

## Purpose
Provides common buffer framing for WiredTiger encryption and decryption. It preserves unencrypted header bytes, stores encrypted result length, calls configured encryptor/decryptor hooks, and reports required destination sizes.

## Important APIs, Types, and Functions
- `__wt_encrypt(session, WT_KEYED_ENCRYPTOR *, skip, in, out)` encrypts bytes after an unencrypted prefix and writes a length field after the prefix.
- `__wt_decrypt(session, WT_ENCRYPTOR *, skip, in, out)` reads the stored length, decrypts encrypted bytes after the prefix and length field, and restores the prefix.
- `__wt_encrypt_size(session, kencryptor, incoming_size, sizep)` computes `incoming_size + size_const + WT_ENCRYPT_LEN_SIZE`.
- Key types include `WT_ITEM`, `WT_ENCRYPTOR`, and `WT_KEYED_ENCRYPTOR`.

## Control Flow
Encryption points `src` after `skip`, reserves a 32-bit stored-size field in the output after the prefix, encrypts into the remaining output buffer sized with the encryptor's constant expansion, asserts the encryptor did not exceed the buffer, stores the final framed length with endian conversion, copies prefix bytes, and sets `out->size`. Decryption reads the framed length, validates it against input size, allocates the output buffer, decrypts payload bytes, copies the prefix, and sets the real decrypted size.

## State and Persistence Behavior
This file defines the durable on-disk/in-memory encrypted item frame: unencrypted prefix, 32-bit encrypted-frame length, then encrypted payload. It does not manage keys directly; it calls the configured encryptor. Endian conversion is applied to the stored length field.

## Dependencies and Integration Points
Used by block/page/log or metadata paths that encrypt `WT_ITEM` buffers. Depends on WiredTiger buffer allocation, endian helpers, encryptor extension APIs, and `WT_ENCRYPT_LEN_SIZE`/`size_const` contracts.

## Risks
Length validation and buffer sizing are security-sensitive. The code assumes encryptors do not expand beyond `size_const` and asserts byte-for-byte bounded behavior. Misaligned access to the stored `uint32_t` or incorrect `skip` values can corrupt framing. Decrypt rejects only `encrypt_len > in->size`; malformed smaller lengths rely on lower decryptor behavior and buffer boundaries.

## Test Signals
Tests should cover round-trip encryption with nonzero skipped headers, big-endian length handling where supported, corrupt length rejection, encryptor `size_const` sizing, zero-length payloads, custom encryptor failure propagation, and fuzzing malformed encrypted buffers.
