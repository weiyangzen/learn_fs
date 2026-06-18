# File Research: sources/os/linux/linux/fs/smb/server/crypto_ctx.h

This header declares KSMBD AEAD crypto context pooling.

Key contents:
- Enum values for AES-GCM and AES-CCM slots.
- `struct ksmbd_crypto_ctx`, containing a list node and AEAD transform array.
- Convenience macros `CRYPTO_GCM(c)` and `CRYPTO_CCM(c)`.
- APIs to find/release contexts and create/destroy the pool.

The enum starts at value 16, so the transform array has unused lower slots; callers use the named enum values only.
