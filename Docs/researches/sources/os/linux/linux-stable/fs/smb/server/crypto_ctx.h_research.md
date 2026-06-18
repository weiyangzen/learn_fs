# File Research: sources/os/linux/linux-stable/fs/smb/server/crypto_ctx.h

Read status: complete.

## Purpose
Declares ksmbd pooled AEAD crypto context structures and APIs.

## Main Contents
- AEAD IDs for AES-GCM and AES-CCM.
- `struct ksmbd_crypto_ctx` with transform array and list node.
- `CRYPTO_GCM()` and `CRYPTO_CCM()` access macros.
- APIs to find/release contexts and create/destroy the pool.

## Dependencies And Role
Included by SMB3 transform crypto code.

## Risks
The transform array indexing depends on enum values and `CRYPTO_AEAD_MAX`; changes must preserve bounds and macro correctness.
