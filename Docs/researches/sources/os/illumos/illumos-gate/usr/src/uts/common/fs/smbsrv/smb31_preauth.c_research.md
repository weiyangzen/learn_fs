# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb31_preauth.c

Implements SMB 3.1.1 preauth integrity hashing.

Key behavior:
- Locates KCF SHA-512 mechanism and stores it in the SMB session.
- Provides SHA-512 digest init/update/final wrappers over KCF.
- Computes the rolling preauth hash as `SHA512(previous_hash || message_bytes)` over an mbuf chain.
- Frees the session preauth mechanism on teardown.

Important dependencies:
- Kernel crypto framework: `crypto_mech2id`, `crypto_digest_init`, `crypto_digest_update`, `crypto_digest_final`.
- Session fields: `preauth_mech`, `smb31_preauth_hashid`, rolling hash buffers.

Notable details:
- Digest update failure cancels the crypto context.
