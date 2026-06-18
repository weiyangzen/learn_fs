# File Research: sources/os/linux/linux/fs/smb/server/crypto_ctx.c

This file implements a small pool of reusable AEAD crypto contexts for SMB3 encryption.

Main behavior:
- Maintains `ctx_list` with spinlock, available-count, idle list, and waitqueue.
- Lazily allocates `struct ksmbd_crypto_ctx` and individual AEAD transforms for `gcm(aes)` and `ccm(aes)`.
- Caps retained contexts around `num_online_cpus()`; excess contexts are freed on release.
- `ksmbd_crypto_ctx_find_gcm()` and `ksmbd_crypto_ctx_find_ccm()` return a context with the requested transform allocated.
- `ksmbd_release_crypto_ctx()` returns a context to the idle list or frees it.
- `ksmbd_crypto_create()` initializes the pool with one idle context; `ksmbd_crypto_destroy()` frees idle contexts.

It is used by `auth.c` encryption/decryption paths to avoid repeatedly allocating AEAD transforms.
