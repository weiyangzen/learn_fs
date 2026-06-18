# sources/user-network-fs/rclone/backend/crypt/cipher.go

## Purpose
This file implements the core cryptographic primitives for rclone's `crypt` backend: filename encryption/obfuscation, stream encryption/decryption, nonce arithmetic, size translation, and ranged decrypt reads. It is security-critical because it defines on-disk/on-remote ciphertext formats and authentication behavior.

## Important APIs, types, and functions
`Cipher` holds data and name keys, EME tweak, AES block, name encryption mode, filename encoding, buffer pool, random source, directory-name behavior, bad-block passthrough flag, and encrypted suffix. `NameEncryptionMode` and `NewNameEncryptionMode` parse name modes. `NewNameEncoding` selects base32, base64, or base32768 filename encodings. `newCipher`, `Key`, `setEncryptedSuffix`, and `setPassBadBlocks` configure cipher state.

Name APIs include `encryptSegment`, `decryptSegment`, `obfuscateSegment`, `deobfuscateSegment`, `EncryptFileName`, `DecryptFileName`, `EncryptDirName`, and `DecryptDirName`. Data APIs include `EncryptData`, `DecryptData`, `DecryptDataSeek`, `EncryptedSize`, and `DecryptedSize`. Internal stream types `encrypter` and `decrypter` implement on-the-fly block processing. `calculateUnderlying` maps plaintext range requests to ciphertext byte ranges.

## Control flow
`Key` derives data key, name key, and name tweak with scrypt unless the password is empty, which deliberately yields zero keys for tests. Standard filename encryption pads each segment with PKCS#7, encrypts with AES-EME using a deterministic tweak, and encodes the ciphertext. Obfuscation performs reversible rune rotations keyed by the name key and quotes special cases. File and directory name methods optionally preserve version suffixes and may skip directory segments.

Data encryption emits a fixed magic header plus a random 24-byte nonce, then reads plaintext in 64 KiB chunks and seals each with NaCl `secretbox`, incrementing the nonce per block. Decryption validates magic, extracts nonce, opens each authenticated block, and returns plaintext. Ranged decryption either seeks an existing underlying `RangeSeeker` or reopens through an `OpenRangeSeek` callback, computes the correct nonce increment, decrypts the first needed block, discards intra-block offset, and enforces limits.

## State and persistence behavior
The encrypted file format is `RCLONE\x00\x00` magic, file nonce, then repeated secretbox blocks with 16-byte authentication overhead and up to 64 KiB data. Encrypted size and decrypted size are deterministic functions of block size and header overhead. Filenames in standard mode are deterministic for a given key and segment; name encryption off appends a configurable suffix, default `.bin`, unless set to `none`. Runtime buffers are recycled through `sync.Pool`.

## Dependencies and integration points
The file depends on Go crypto AES/rand/cipher packages, `x/crypto/nacl/secretbox`, `x/crypto/scrypt`, `rfjakob/eme`, local `pkcs7`, rclone accounting/range interfaces, readers helpers, version suffix helpers, and base32768. It exposes interfaces expected by higher-level crypt backend object operations.

## Risks and edge cases
This code is security-sensitive. Deterministic filename encryption leaks equality of names. Empty password intentionally creates zero keys for tests and must not be confused with secure configuration. `passBadBlocks` converts authentication failures into zero-filled plaintext, which is useful for recovery but dangerous for integrity. Ranged reads depend on exact `calculateUnderlying` math and nonce addition; off-by-one errors corrupt data or authentication. `deobfuscateSegment` leaves dangling quote state unchecked. `setEncryptedSuffix` silently prefixes a missing dot after logging, which may mask config mistakes. Buffer pool misuse after `finish` would be hazardous, though methods guard with `fh.err`.

## Test signals
`cipher_test.go` is extensive: it covers mode parsing, filename encodings, encryption/decryption vectors for base32/base64/base32768, obfuscation, suffix behavior, encrypted/decrypted size math, nonce arithmetic, stream encryption/decryption across buffer sizes and large data, truncated/corrupt input errors, ranged seek/limit behavior, close semantics, bad-block passthrough, and scrypt key vectors.
