# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_signing.c

Implements SMB2/SMB3 message signing.

Key behavior:
- Initializes per-session signing mechanism based on negotiated signing algorithm: HMAC-SHA256, AES-CMAC, or AES-GMAC.
- Derives per-user signing keys from the session key:
  - SMB2 uses the first 16 bytes, padded/truncated.
  - SMB3 uses KDF labels/contexts.
  - SMB 3.1.1 uses the preauth hash value as KDF context.
- Enables/checks signing flags based on client and server security modes.
- Builds AES-GMAC IVs from message ID, direction, and cancel flag.
- Computes signatures over the SMB2 header plus payload while zeroing the signature field in a temporary header copy.
- Verifies incoming request signatures and writes outgoing reply signatures.

Important dependencies:
- KDF and MAC helpers: `smb3_kdf`, `smb2_mac_uio`, `smb2_sign_init_hmac_param`, `smb3_sign_init_gmac_param`.
- Session/user signing state and keys.

Notable details:
- Commands with zero session ID are not signature-checked.
- If a required crypto mechanism is unavailable, verification fails and replies may be left unsigned, likely causing client disconnect.
