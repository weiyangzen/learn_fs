# File Research: sources/os/linux/linux-stable/fs/smb/server/smbfsctl.h

## Summary
Defines SMB/CIFS/SMB2 FSCTL and reparse-tag numeric constants used by ksmbd IOCTL handling.

## Main Responsibilities
- List filesystem, pipe, copychunk, network-interface, validate-negotiate, sparse, compression, object-id, reparse-point, and DFS FSCTL operation codes.
- Define common reparse tags and WSL/Linux reparse tags in little-endian form.

## Cross-File Interactions
Included by SMB2 IOCTL handling and reparse/symlink logic. Constants such as `FSCTL_VALIDATE_NEGOTIATE_INFO`, `FSCTL_QUERY_NETWORK_INTERFACE_INFO`, `FSCTL_COPYCHUNK`, and WSL reparse tags drive protocol-specific dispatch.

## Risks
These values are wire protocol constants. Any typo or endian mismatch causes clients to receive incorrect IOCTL behavior or incompatible reparse metadata.
