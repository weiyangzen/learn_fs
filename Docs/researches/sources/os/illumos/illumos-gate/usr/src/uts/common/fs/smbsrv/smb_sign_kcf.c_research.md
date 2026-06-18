# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_sign_kcf.c

Kernel Cryptographic Framework backend for SMB signing and MAC generation. The file is the kernel counterpart to the user-space fake SMB server signing implementation.

`find_mech` resolves named crypto mechanisms with `crypto_mech2id`, logs unavailable mechanisms, and stores the mechanism type into `smb_crypto_mech_t`. SMB1 signing uses MD5 helpers: `smb_md5_getmech`, `smb_md5_init`, `smb_md5_update`, and `smb_md5_final`. Updates wrap raw buffers in `crypto_data_t`; update failure cancels the KCF context.

SMB2/SMB3 mechanism helpers expose SHA256 HMAC, AES-CMAC, and AES-GMAC lookup. `smb2_sign_init_hmac_param` sets the HMAC output length parameter, while `smb3_sign_init_gmac_param` initializes KCF GMAC parameters with an IV and no AAD.

The shared `smb2_mac` helper performs one-shot `crypto_mac` with a raw key measured in bits and a caller-supplied raw output buffer. Public wrappers support scatter/gather UIO input (`smb2_mac_uio`) and contiguous raw input (`smb2_mac_raw`). The common SMB2 signature case writes a 16-byte digest/signature buffer, while the raw helper accepts caller-specified MAC length.

This file contains no SMB protocol parsing. It is a cryptographic adapter used by higher-level SMB1/SMB2 signing code and depends on `sys/crypto/api.h`, `smb_kproto.h`, and `smb_kcrypt.h`.
