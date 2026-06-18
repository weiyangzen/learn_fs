# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_spnego.h

## Purpose

Declares the CIFS SPNEGO upcall ABI message, version, key type, and key acquisition helper.

## Main Contents

- Defines `CIFS_SPNEGO_UPCALL_VERSION` as `2`.
- Defines `struct cifs_spnego_msg`:
  - version
  - flags
  - session-key length
  - security-blob length
  - flexible payload containing session key followed by security blob
- Declares external key type `cifs_spnego_key_type`.
- Declares `cifs_get_spnego_key()`.

## Integration Notes

- Used by CIFS session setup and `cifs_spnego.c`.
- The structure is part of the contract with the userspace request-key helper.
