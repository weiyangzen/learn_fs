# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_encrypt.c

Implements SMB3 encryption/decryption orchestration around SMB3 transform headers.

Key behavior:
- Initializes nonce salt/fixed bytes per user and generates monotonically unique nonces until an overflow guard threshold.
- Initializes AES-CCM or AES-GCM session mechanism from negotiated cipher ID.
- Derives per-user encryption/decryption keys:
  - SMB 3.1.1 uses cipher-specific key size and preauth-hash KDF contexts.
  - Older SMB3 uses AES-128 CCM labels/contexts.
- Decodes and validates SMB3 transform headers.
- Decrypts incoming encrypted requests by authenticating transform header fields, looking up transform session ID, validating key length, and decrypting ciphertext plus signature tag into cleartext.
- Encrypts outgoing replies by generating nonce, encoding transform header, encrypting cleartext into ciphertext, and patching the resulting signature/tag into the transform header.
- Frees session encryption mechanism on teardown.

Important dependencies:
- Crypto backend: `smb3_crypto_init_ccm_param`, `smb3_crypto_init_gcm_param`, `smb3_encrypt_init`, `smb3_decrypt_init`, `smb3_encrypt_uio`, `smb3_decrypt_uio`.
- KDF: `smb3_kdf`.
- Session/user transform lookup: `smb_session_lookup_ssnid`.

Notable details:
- Decrypt errors return distinct negative values for DTrace visibility, and any non-zero result drops the connection.
- Transform header protocol ID is asserted earlier in request dispatch.
