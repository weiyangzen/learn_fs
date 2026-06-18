# File Research: sources/os/linux/linux-stable/fs/nfs/Makefile

Build rules for the Linux NFS client.

Key behavior:
- Builds `nfs.o` from core client, directory, inode, superblock, I/O, read/write, mount, namespace, tracing, context, and export sources.
- Adds optional objects for root NFS, sysctl, FS-Cache integration, and local I/O.
- Builds version-specific modules: `nfsv2.o`, `nfsv3.o`, and `nfsv4.o`.
- Adds NFSv4 optional components for legacy DNS, sysctl, v4.0, and v4.2.
- Descends into pNFS layout directories based on config: filelayout, blocklayout, flexfilelayout.
