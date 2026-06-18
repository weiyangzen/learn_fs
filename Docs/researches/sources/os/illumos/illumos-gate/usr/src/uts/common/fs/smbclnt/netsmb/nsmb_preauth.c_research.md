# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_preauth.c

## Purpose

`nsmb_preauth.c` implements SMB 3.1.1 preauthentication integrity hashing for the SMB client.

## Main Interfaces

It exports `nsmb_preauth_init()` and `nsmb_preauth_calc()`.

## Behavior And Data Flow

`nsmb_preauth_init()` obtains the SHA512 mechanism and stores it in the virtual circuit's preauth mechanism field. Failure maps to `EAUTH`.

`nsmb_preauth_calc()` creates a SHA512 digest context, first digests the previous 64-byte preauth hash value, then digests every mblk segment of the current SMB message, and finally writes the new 64-byte hash value.

## Dependencies

The file depends on `smb_vc_t` preauth fields, mblk chains, and SHA512 helper functions from `nsmb_sign_kcf.c` or the user-space crypto equivalent declared in `nsmb_kcrypt.h`.

## Research Notes

This code is short but security-critical. It is used during SMB 3.1.1 negotiation and session setup before signing keys are derived. Failure accounting is handled by callers in `smb2_smb.c`.
