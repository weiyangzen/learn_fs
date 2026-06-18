# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_sign.c

## Purpose

`smb2_sign.c` implements SMB2/3 message signing and signature verification for the SMB client. It chooses HMAC-SHA256 for SMB2.x and AES-CMAC for SMB3.x, with SMB 3.1.1 signing keys derived from the preauth hash.

## Main Interfaces

The exported functions are `smb2_sign_init()`, `smb2_rq_sign()`, and `smb2_rq_verify()`. The internal MAC engine is `smb2_compute_MAC()`, parameterized by `smb_mac_ops_t`.

## Behavior And Data Flow

`smb2_sign_init()` obtains the appropriate crypto mechanism, allocates a 16-byte MAC key, and derives it from the session key. For SMB2.x, the key is the first 16 bytes of the session key, padded or truncated. For SMB3.0/3.0.2, it uses `nsmb_kdf()` with label `SMB2AESCMAC` and context `SmbSign`. For SMB3.1.1, it uses label `SMBSigningKey` and the current preauth hash as context.

`smb2_compute_MAC()` copies the SMB2 header, zeroes the 16-byte signature field at offset 48, MACs that modified header, MACs the remainder of the first mblk, then MACs all following mblks. The final signature is written to the caller-provided buffer.

`smb2_rq_sign()` writes the computed signature directly into the request header. On crypto failure it zeros the signature field. `smb2_rq_verify()` computes the expected signature for a reply and compares it to the on-wire signature, returning `EBADRPC` on mismatch.

## Dependencies

The file depends on crypto helper functions from `nsmb_kcrypt.h`, SMB virtual circuit session/signing fields, SMB2 header layout constants, mblk chains, SMB request structures, and dialect macros.

## Research Notes

Security-sensitive details include zeroing exactly the signature field before MAC calculation, using the correct signing algorithm by dialect, refusing to proceed on MAC computation failure, and deriving SMB3.1.1 keys only after valid preauth hashing. The compare uses `bcmp()`, so this is not constant-time.
