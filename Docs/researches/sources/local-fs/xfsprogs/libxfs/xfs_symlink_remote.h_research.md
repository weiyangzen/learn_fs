# File Research: sources/local-fs/xfsprogs/libxfs/xfs_symlink_remote.h

This header declares the remote symlink encode/decode and mutation helpers from `xfs_symlink_remote.c`.

The interface covers block-count calculation, CRC header setup/checking, local-to-remote conversion during fork format changes, inline symlink verification, remote symlink read, target write, and remote truncation. Callers must supply locked inodes and transactions according to the individual function semantics in the implementation.

The header is small but important because remote symlink code participates in inode fork formatting, bmap allocation/unmapping, metadata buffer verification, and transaction logging.
