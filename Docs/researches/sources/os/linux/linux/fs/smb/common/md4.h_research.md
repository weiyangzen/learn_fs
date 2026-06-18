# File Research: sources/os/linux/linux/fs/smb/common/md4.h

## Scope
Read completely: 27 lines. This header declares the CIFS MD4 context and API.

## Purpose
`md4.h` exposes constants, state, and functions for the SMB common MD4 implementation in `cifs_md4.c`.

## Contents
Constants:
- `MD4_DIGEST_SIZE` = 16
- `MD4_HMAC_BLOCK_SIZE` = 64
- `MD4_BLOCK_WORDS` = 16
- `MD4_HASH_WORDS` = 4

State:
- `struct md4_ctx` with four hash words, sixteen block words, and a 64-bit byte counter.

Functions:
- `cifs_md4_init()`
- `cifs_md4_update()`
- `cifs_md4_final()`

## Integration Points
Included by SMB common/client authentication code needing the CIFS MD4 implementation. The implementation exports the three functions as GPL symbols.

## Notable Details
The comment says “Common values for ARC4 Cipher Algorithm,” but the definitions are MD4-specific. This appears to be a stale or copied comment.

## Research Takeaways
`md4.h` is a minimal compatibility API for legacy MD4 hashing in SMB code.
