# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_kdf.c

Implements SMB3 key derivation using NIST SP800-108 counter-mode KDF with HMAC-SHA256.

Key behavior:
- Builds `counter || label || 0x00 || context || L` with big-endian counter and bit-length.
- Enforces label and context maximum sizes matching SMB3 use cases.
- Uses SMB HMAC mechanism setup and raw MAC helper to generate derived keys.
- Supports 128-bit and 256-bit derived key lengths through caller-supplied `keylen`.

Important dependencies:
- `smb2_hmac_getmech`, `smb2_sign_init_hmac_param`, `smb2_mac_raw`.

Notable details:
- Comments document the SMB 3.0.2 and SMB 3.1.1 labels/contexts for signing, application, encryption, and decryption keys.
