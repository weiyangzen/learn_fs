# File Research: sources/os/linux/linux-stable/fs/nfs/internal.h

## Purpose
Central private header for the Linux NFS client implementation. It ties together mount parsing, client/server lifecycle, page I/O, namespace/submount handling, localio, NFSv2/v3/v4 procedure tables, inode/file operations, commit/writeback helpers, and small inline utilities shared across `fs/nfs`.

## Main Interfaces
- Defines `struct nfs_client_initdata`, the construction input for `nfs_client` objects: address, hostname, protocol, NFS module, network namespace, timeouts, credentials, transport security, and connect/reconnect timeouts.
- Defines `struct nfs_fs_context`, the in-kernel mount context used by NFS fs_context code. It stores parsed mount options, server/mount-server addresses, auth flavor selection, transport security, clone/submount data, and resulting `nfs_server`.
- Defines `struct nfs_mount_request` for the v2/v3 MOUNT protocol client in `mount_clnt.c`.
- Declares the broad internal NFS API: client allocation/probing, server creation/cloning, procfs hooks, page cache slab setup, pgio setup, file operations, inode lifecycle, namespace automount/submount helpers, read/write/commit paths, NFSv4 client/state helpers, and direct I/O request state.
- Declares `struct nfs_direct_req`, the direct I/O completion and commit tracker with refcounting, I/O counters, completion, error/count fields, and direct-write/read flags.

## Important Inline Helpers
- Attribute and mountpoint helpers:
  - `nfs_attr_check_mountpoint()` marks fattrs as mountpoints when fsids differ.
  - `nfs_attr_use_mounted_on_fileid()` decides whether `mounted_on_fileid` should be used for mountpoint/referral cases.
  - `nfs_lookup_is_soft_revalidate()` detects positive dentries eligible for soft revalidation.
- Mount/logging helpers:
  - `nfs_fc2context()` extracts `nfs_fs_context`.
  - `nfs_errorf`, `nfs_invalf`, `nfs_warnf` variants route messages through fs_context logging when available.
- I/O and sizing helpers:
  - `flags_to_mode()` maps open flags to `FMODE_READ`, `FMODE_WRITE`, `FMODE_EXEC`.
  - `nfs_file_block_o_direct()` clears `NFS_INO_ODIRECT` and waits for DIO.
  - `nfs_block_bits()`, `nfs_block_size()`, and `nfs_io_size()` clamp and align block/read/write sizes.
  - `nfs_super_set_maxbytes()` clamps server max file size to Linux limits.
  - `nfs_folio_length()` computes valid data length for a folio relative to inode size.
  - `nfs_page_array_len()` computes page-vector length for base+len.
- Write/commit helpers:
  - `nfs_folio_mark_unstable()` accounts unstable writeback and dirties inode state.
  - `nfs_write_verifier_cmp()` / `nfs_write_match_verf()` compare commit verifiers.
  - `nfs_clear_pnfs_ds_commit_verifiers()` clears pNFS commit verifier state when v4 is enabled.
- Error helpers:
  - `nfs_error_is_fatal()` and `nfs_error_is_fatal_on_server()` classify errors for retry/recovery behavior.
  - `nfs_current_task_exiting()` wraps `PF_EXITING`.
- Misc:
  - `nfs_should_remove_suid()` implements NFS-specific suid/sgid stripping.
  - `nfs_timespec_to_change_attr()` converts timestamps to a synthetic change attribute.
  - `nfs_stateid_hash()` hashes NFSv4 stateids.
  - `nfs_set_port()` applies default/user port selection to socket addresses.
  - `nfs_igrab_and_active()` / `nfs_iput_and_deactive()` pair inode refs with superblock active refs.

## Configuration-Dependent Behavior
- `CONFIG_NFS_V4` gates v4 XDR/proc declarations and pNFS commit verifier handling.
- `CONFIG_NFS_V4_SECURITY_LABEL` gates NFSv4 label allocation/copy/cache invalidation.
- `CONFIG_NFS_LOCALIO` exposes local I/O probe/open/read-write/commit hooks; otherwise stubs return disabled behavior.
- `CONFIG_PROC_FS`, `CONFIG_NFS_FSCACHE`, and `CONFIG_MIGRATION` provide no-op or feature-specific hooks.

## Dependencies and Coupling
This header is intentionally high-coupling: it is the contract between NFS mount setup, RPC procedure modules, inode/file/page I/O code, pNFS, localio, and NFSv4 state management. Changes here affect many translation units and should be treated as ABI-like within `fs/nfs`.

## Research Notes
- The file is not an implementation module but is behaviorally important because many static inline helpers encode policy, especially I/O sizing, fatal error classification, suid stripping, localio stubs, and mountpoint detection.
- The localio declarations correspond directly to `localio.c`.
- The `io.c` declarations and `nfs_file_block_o_direct()` form the buffered-vs-direct serialization contract.
