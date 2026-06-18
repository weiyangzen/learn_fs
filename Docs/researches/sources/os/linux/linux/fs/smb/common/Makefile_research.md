# File Research: sources/os/linux/linux/fs/smb/common/Makefile

## Scope
Read completely: 6 lines. This Makefile builds shared SMB filesystem common code.

## Purpose
The file declares build output for routines shared by SMB client and server code.

## Contents
- SPDX: `GPL-2.0-only`.
- Comment: “Makefile for Linux filesystem routines that are shared by client and server.”
- Build rule: `obj-$(CONFIG_SMBFS) += cifs_md4.o`.

## Integration Points
When `CONFIG_SMBFS` is enabled, `fs/smb/common/cifs_md4.c` is built into the SMB common object set.

## Research Takeaways
This Makefile currently contributes only the CIFS-specific MD4 implementation to the common SMB build.
