# File Research: sources/os/linux/linux-stable/fs/nfsd/acl.h

Purpose: Declares common NFSv4 ACL handling APIs for NFSD.

Key responsibilities:
- Forward declares NFSv4 ACL, service request/filehandle, attrs, and file type structures.
- Declares helpers for NFSv4 ACL byte sizing, who-type decoding, and who field encoding.
- Declares server-side ACL fetch and ACL-to-attribute conversion.
- Declares POSIX ACL range sorting.

Integration:
- Used by NFSD NFSv4 ACL implementation and XDR/attribute conversion paths.

Risks and notes:
- Header carries a BSD-style historical license block while source tree uses kernel-compatible terms.
