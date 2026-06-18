# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/Makefile

This Makefile builds the DragonFlyBSD `smbfs` kernel module. It pulls in SMB network protocol support from `netproto/smb`, crypto DES code, kernel helpers, and libkern MD4 support.

The module sources include the net SMB connection/device/request/crypto/iod files plus the SMBFS VFS layer: `smbfs_vfsops.c`, `smbfs_node.c`, `smbfs_io.c`, `smbfs_vnops.c`, `smbfs_subr.c`, and `smbfs_smb.c`. DES source files are added explicitly for authentication support.

It defines generated option headers when not building inside a kernel build directory: `opt_inet.h` is generated according to `SMB_INET`, and `opt_netsmb.h` always defines `NETSMB`. The module is then included through `bsd.kmod.mk`.
