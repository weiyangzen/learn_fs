# File Research: sources/os/linux/linux-stable/fs/smb/common/Makefile

## Summary
Build file for SMB routines shared by client and server code.

## Behavior
When `CONFIG_SMBFS` is enabled, the common SMB object list includes `cifs_md4.o`.

## Integration Notes
This Makefile is minimal but determines whether the local MD4 implementation in `cifs_md4.c` is built into the shared SMB common code. Changes affect both client/server consumers that depend on the common SMB configuration.
