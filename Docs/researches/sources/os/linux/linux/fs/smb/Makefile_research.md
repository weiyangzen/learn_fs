# File Research: sources/os/linux/linux/fs/smb/Makefile

Top-level Kbuild dispatcher for SMB subdirectories.

It builds `common/` under `CONFIG_SMBFS`, `smbdirect/` under `CONFIG_SMBDIRECT`, `client/` under `CONFIG_CIFS`, and `server/` under `CONFIG_SMB_SERVER`. There is no local object logic beyond subdirectory selection.
