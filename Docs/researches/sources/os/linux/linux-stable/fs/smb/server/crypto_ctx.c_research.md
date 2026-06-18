# File Research: sources/os/linux/linux-stable/fs/smb/server/crypto_ctx.c

Read status: complete.

## Purpose
Provides a small reusable pool of ksmbd AEAD crypto contexts for SMB3 encryption/decryption.

## Main Responsibilities
- Allocate AES-GCM and AES-CCM `crypto_aead` transforms on demand.
- Maintain an idle context list protected by a spinlock and wait queue.
- Limit retained contexts relative to online CPU count.
- Release contexts back to the pool or free excess contexts.
- Initialize and destroy the global crypto context pool.

## Dependencies And Role
Used by `auth.c` transform encryption/decryption to avoid repeated AEAD allocation overhead.

## Risks
Pool accounting and wait behavior must remain correct under memory pressure and concurrent encrypted I/O. The enum values are sparse, so array bounds checks in lookup are important.
