# File Research: sources/os/linux/linux/fs/nfsd/acl.h

Declares common NFSD NFSv4 ACL helpers.

Key behavior:
- Forward-declares core NFSD ACL-related types.
- Declares helpers to compute ACL byte length, parse/get NFSv4 ACL who-type values, and encode who fields.
- Declares server-side conversion helpers:
  - `nfsd4_get_nfs4_acl()` to retrieve an NFSv4 ACL for a dentry.
  - `nfsd4_acl_to_attr()` to convert an NFSv4 ACL into NFSD attributes.
  - `sort_pacl_range()` to sort a POSIX ACL subrange.

Important interactions:
- Used by NFSD NFSv4 ACL and XDR handling code.
- Carries a permissive historical license notice in the header comment, while the file itself is not tagged with a Linux SPDX line.
