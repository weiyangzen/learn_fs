# File Research: sources/os/linux/linux/fs/nfs/internal.h

## Purpose
Central private header for the Linux NFS client. It connects mount parsing, client/server setup, page I/O, namespace/submount handling, LOCALIO, NFSv2/v3/v4 procedure plumbing, inode/file operations, writeback/commit helpers, and direct I/O state.

## Main Interfaces
- Defines `struct nfs_client_initdata`, the input used to construct `nfs_client` objects: server address, hostname, protocol, NFS subversion module, net namespace, credentials, transport security, connection counts, and timeout values.
- Defines `struct nfs_fs_context`, the in-kernel mount context for parsed mount options, server and mount-server addresses, auth flavor selection, transport security, clone/submount state, and resulting `nfs_server`.
- Defines `struct nfs_mount_request`, consumed by `mount_clnt.c` for v2/v3 MOUNT protocol lookups.
- Declares internal NFS APIs for client allocation/probing, server creation/cloning, procfs setup, page cache slab setup, pgio operations, directory/file/inode operations, namespace automounts, read/write/commit paths, NFSv4 state/client helpers, and direct I/O.
- Declares `struct nfs_direct_req`, the direct I/O refcounted completion and commit tracker.
- Adds `struct file_kattr` forward declaration and `nfs_fileattr_get()` for file attribute support in inode operation tables.

## Important Inline Policy
- Mountpoint and referral handling: `nfs_attr_check_mountpoint()`, `nfs_attr_use_mounted_on_fileid()`, `nfs_lookup_is_soft_revalidate()`.
- Mount diagnostics: `nfs_errorf`, `nfs_invalf`, `nfs_warnf`, and fs_context-aware variants.
- I/O sizing and serialization: `flags_to_mode()`, `nfs_file_block_o_direct()`, `nfs_block_bits()`, `nfs_block_size()`, `nfs_io_size()`, `nfs_super_set_maxbytes()`, `nfs_folio_length()`, `nfs_page_array_len()`.
- Writeback and commit helpers: `nfs_folio_mark_unstable()`, write verifier comparison, pNFS DS commit verifier clearing.
- Error classification: `nfs_error_is_fatal()` and `nfs_error_is_fatal_on_server()`.
- Miscellaneous helpers: NFS-specific suid/sgid stripping, timestamp-to-change-attribute conversion, NFSv4 stateid hashing, default port selection, and inode/superblock active-reference pairing.

## Configuration-Dependent Behavior
- `CONFIG_NFS_V4` gates v4 XDR/procedure declarations and pNFS verifier helpers.
- `CONFIG_NFS_V4_SECURITY_LABEL` gates security label allocation/copy/cache invalidation helpers.
- `CONFIG_NFS_LOCALIO` exposes local file open, local pgio, local commit, and local server probe hooks; otherwise stubs return disabled behavior.
- `CONFIG_PROC_FS`, `CONFIG_NFS_FSCACHE`, and `CONFIG_MIGRATION` provide feature-specific or no-op paths.

## Dependencies and Coupling
This header is deliberately high-coupling. It is the contract among NFS mount setup, RPC procedure modules, VFS inode/file operations, page I/O, pNFS, LOCALIO, and NFSv4 state management. Changes here can affect many `fs/nfs` translation units.

## Research Notes
The header contains real behavioral policy despite being mostly declarations. The subtle areas are I/O size alignment, buffered-vs-direct serialization, fatal error classification, suid/sgid stripping, mountpoint detection, and LOCALIO stubbing.
