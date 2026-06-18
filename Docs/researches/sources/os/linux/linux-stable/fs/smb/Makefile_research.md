# File Research: sources/os/linux/linux-stable/fs/smb/Makefile

## Purpose

Top-level Kbuild dispatch for SMB-related filesystem subdirectories.

## Main Contents

- Builds `common/` when `CONFIG_SMBFS` is enabled.
- Builds `smbdirect/` when `CONFIG_SMBDIRECT` is enabled.
- Builds `client/` when `CONFIG_CIFS` is enabled.
- Builds `server/` when `CONFIG_SMB_SERVER` is enabled.

## Integration Notes

This file connects the Kconfig aggregation in `fs/smb/Kconfig` to the concrete SMB common, client, server, and RDMA transport build directories.
