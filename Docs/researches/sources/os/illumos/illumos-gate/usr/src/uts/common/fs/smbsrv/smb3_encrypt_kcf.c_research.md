# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_encrypt_kcf.c

Kernel KCF backend for SMB3 encryption helpers.

Key behavior:
- Finds AES-CCM and AES-GCM KCF mechanisms.
- Initializes CCM parameters with MAC size, nonce, auth data, and data size.
- Initializes GCM parameters with IV, tag bits, and AAD.
- Stores raw crypto keys in `smb_enc_ctx_t`.
- Encrypts/decrypts whole messages using KCF `crypto_encrypt()` / `crypto_decrypt()` over UIO scatter/gather data.
- Provides a context cleanup wrapper.

Important dependencies:
- Kernel crypto framework: `crypto_mech2id`, `crypto_encrypt`, `crypto_decrypt`, `crypto_cancel_ctx`.
- `smb_kcrypt.h` crypto abstractions.

Notable details:
- This file intentionally contains almost no SMB protocol knowledge beyond shared crypto constants.
- Crypto context templates are marked as future work.
