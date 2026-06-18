# sources/user-network-fs/libsmb2/lib/hmac-md5.c

## Purpose
`hmac-md5.c` implements the RFC 2104 HMAC-MD5 construction used by NTLM/SMB authentication paths that require MD5-based keyed digests. It is a small one-shot helper around the repository's MD5 implementation.

## Important APIs, Types, and Functions
The exported function is `smb2_hmac_md5(unsigned char *text, int text_len, unsigned char *key, unsigned int key_len, unsigned char *digest)`. It uses `struct MD5Context` plus `MD5Init()`, `MD5Update()`, and `MD5Final()` from `md5.h`. The caller supplies the message buffer, key buffer, and a 16-byte digest output buffer.

## Control Flow
If the key is longer than the 64-byte MD5 block size, the function first hashes it to a 16-byte temporary key. It zeroes 65-byte inner and outer pad arrays, copies the key into each, XORs the first 64 bytes with `0x36` and `0x5c`, computes the inner digest over `ipad || text`, then computes the final digest over `opad || inner_digest`.

## State and Persistence Behavior
The function keeps all state on the stack and writes only to the caller-provided `digest`. It performs no heap allocation and no persistence. Temporary key and pad buffers contain key material until the stack frame is reused; they are not explicitly wiped.

## Dependencies and Integration Points
It depends on `compat.h`, `md5.h`, optional `strings.h`, and the declaration in `hmac-md5.h`. In libsmb2 this is part of the legacy NTLM crypto support surface alongside MD4/MD5/HMAC-SHA helpers and is expected to produce exactly 16 bytes.

## Risks and Edge Cases
The API accepts mutable pointers even though the text and key are not intentionally modified. `text_len` is signed while the MD5 update API receives the value as a length, so negative lengths from callers would be hazardous. The function assumes non-NULL buffers and an adequately sized digest. MD5 is cryptographically obsolete outside protocols such as NTLM that require it for compatibility.

## Test Signals
Use RFC 2104 HMAC-MD5 known-answer vectors, a key longer than 64 bytes, an empty message, an empty key, and a normal NTLM-sized key/message. Memory-safety tests should include NULL/invalid caller behavior at API boundaries if the surrounding library promises defensive checks elsewhere.
