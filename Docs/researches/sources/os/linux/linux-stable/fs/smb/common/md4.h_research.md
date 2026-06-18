# File Research: sources/os/linux/linux-stable/fs/smb/common/md4.h

## Summary
Declares the CIFS MD4 context, digest/block size constants, and exported MD4 helper prototypes.

## Main Interfaces
- Constants: `MD4_DIGEST_SIZE`, `MD4_HMAC_BLOCK_SIZE`, `MD4_BLOCK_WORDS`, `MD4_HASH_WORDS`.
- `struct md4_ctx`: stores four hash words, sixteen block words, and byte count.
- Prototypes: `cifs_md4_init()`, `cifs_md4_update()`, `cifs_md4_final()`.

## Integration Notes
Used by `cifs_md4.c` and any SMB common/client code needing legacy MD4 hashing. The context layout is private to this implementation but exposed through the header for stack or embedded allocation.

## Risks
The API exposes a legacy cryptographic primitive. Callers must not use it for new security properties beyond required SMB/NTLM compatibility.
