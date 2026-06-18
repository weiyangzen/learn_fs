# File Research: sources/os/linux/linux-stable/fs/smb/server/asn1.h

Read status: complete.

## Purpose
Declares ksmbd SPNEGO ASN.1 decode and blob-building helpers.

## Main Contents
- Prototypes for `ksmbd_decode_negTokenInit()` and `ksmbd_decode_negTokenTarg()`.
- Prototypes for NTLMSSP SPNEGO negotiation/auth response blob construction.

## Dependencies And Role
Used by SMB2 session setup/authentication code to bridge wire security blobs to `asn1.c`.

## Risks
Prototype changes affect authentication call sites and buffer ownership expectations for allocated SPNEGO blobs.
