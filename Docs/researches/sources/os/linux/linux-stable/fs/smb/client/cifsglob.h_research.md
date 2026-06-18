# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsglob.h

Read status: complete.

## Purpose

Central shared header for the CIFS/SMB client. It defines global constants, core state structures, dialect operation callbacks, mount/session/tcon/inode/file/request data structures, lock ordering documentation, global externs, and inline helpers.

## Main Responsibilities

- Define protocol and client-wide constants for paths, ports, buffers, credits, timeouts, channels, and cache sizing.
- Define connection/session/tree/open/inode/MID/I/O state structures.
- Declare the dialect abstraction table `struct smb_version_operations`.
- Provide helpers for credits, MID generation, path delimiters, DFS metadata, refcounting, cache-state checks, reconnect scheduling, and scatterlist setup.
- Document lock ordering for the CIFS client.

## Major Type Groups

### Protocol and Mount Constants

- Ports:
  - `CIFS_PORT`
  - `RFC1001_PORT`
- Request/concurrency constants:
  - `CIFS_MAX_REQ`
  - `SMB2_MAX_CREDITS_AVAILABLE`
  - `MAX_COMPOUND`
- Timeouts:
  - `CIFS_DEF_ACTIMEO`
  - `CIFS_MAX_ACTIMEO`
  - `SMB3_MAX_HANDLE_TIMEOUT`
  - echo interval bounds
- Size limits:
  - `CIFS_MAX_WSIZE`
  - `CIFS_MAX_RSIZE`
  - RFC1002-size variants
  - non-POSIX default read/write sizes

### Enums

- Connection state:
  - `enum statusEnum`
- Session state:
  - `enum ses_status_enum`
- Tree state:
  - `enum tid_status_enum`
- Security mechanism:
  - `enum securityEnum`
- Upcall target:
  - `enum upcall_target_enum`
- Reparse and symlink policy:
  - `enum cifs_reparse_type`
  - `enum cifs_symlink_type`

### Core Structures

- `struct session_key`
  - Authentication/session-key byte buffer.

- `struct cifs_secmech`
  - SMB3 AEAD encrypt/decrypt transforms.

- `struct ntlmssp_auth`
  - NTLMSSP flags, challenge/ciphertext, and session-key behavior.

- `struct cifs_open_info_data`
  - File metadata query result container, including reparse buffers, WSL EAs, POSIX info, symlink targets, and owner/group SIDs.

- `struct smb_rqst`
  - Complete SMB request representation: kvecs, data iterator, and encryption buffer.

- `struct smb_version_operations`
  - Large dialect callback table for SMB1/2/3 differences.
  - Covers send/receive, signing, credits, negotiate/session/tree connect, path/file queries, open/close/read/write, directory enumeration, oplocks, locks, copy offload, ACLs, xattrs, transform headers, reparse handling, fiemap, llseek, and POSIX node creation.

- `struct TCP_Server_Info`
  - Per-server/socket state.
  - Tracks transport status, socket addresses, credits, pending MIDs, signing/encryption negotiation, cryptographic keys, RDMA, compression, reconnect state, multichannel primary/channel state, DFS state, and work items.

- `struct cifs_ses`
  - Per-authenticated SMB session state.
  - Tracks user/domain/passwords, security type, signing/encryption keys, capabilities, interface list, multichannel channel array, DFS root session, and NLS table.

- `struct cifs_tcon`
  - Per-tree/share connection state.
  - Tracks share capabilities, flags, statistics, open files, pending opens, cached directory handles, DFS integration, fscache state, durable/persistent handle policy, POSIX extensions, witness, and snapshot metadata.

- `struct tcon_link`
  - Refcounted tree-connection holder keyed by uid for multiuser mounts.

- `struct cifs_open_parms`
  - Open request parameter bundle used by dialect open routines.

- `struct cifs_fid`
  - SMB1 netfid or SMB2 persistent/volatile file id plus lease key and open state.

- `struct cifsFileInfo`
  - Per-open-file state, including inode/tcon links, locks, fid, reconnect/deferred-close/oplock work, search info, and symlink target.

- `struct cifsInodeInfo`
  - CIFS inode extension embedded around `struct netfs_inode`.
  - Tracks oplock/cache state, open files, lock lists, DOS attrs, lease key, timestamps, deferred closes, symlink target, and reparse tag.

- `struct mid_q_entry`
  - Pending request/response tracking object.
  - Holds MID id, credits, response buffer, callbacks, state flags, timing/stat fields, and synchronization.

- `struct cifs_io_request` / `struct cifs_io_subrequest`
  - Netfs-integrated read/write request and subrequest state.

## Important Macros and Helpers

- `CIFS_SB()`
  - `_Generic` helper to retrieve `struct cifs_sb_info *` from inode, dentry, superblock, file, or CIFS inode.

- `cifs_sb_flags()`
  - Atomic read of mount flags.

- `CIFS_DIR_SEP()` and `convert_delimiter()`
  - Path delimiter policy helpers.

- Credit helpers:
  - `add_credits()`
  - `add_credits_and_wake_if()`
  - `set_credits()`
  - `adjust_credits()`
  - `has_credits()`

- MID helpers:
  - `get_next_mid64()`
  - `get_next_mid()`
  - `revert_current_mid()`
  - `mid_execute_callback()`
  - `smb_get_mid()`
  - `release_mid()`

- Cache helpers:
  - `CIFS_CACHE_READ()`
  - `CIFS_CACHE_HANDLE()`
  - `CIFS_CACHE_WRITE()`
  - `cifs_reset_oplock()`

- Reconnect helpers:
  - `cifs_queue_server_reconn()`
  - `cifs_requeue_server_reconn()`

- DFS helpers:
  - `free_dfs_info_param()`
  - `free_dfs_info_array()`
  - `dfs_src_pathname_equal()`
  - `is_tcon_dfs()`
  - `cifs_is_referral_server()`

- Error classification:
  - `is_interrupt_error()`
  - `is_retryable_error()`
  - `is_replayable_error()`

- Security flag constants:
  - `CIFSSEC_MAY_*`
  - `CIFSSEC_MUST_*`
  - `CIFSSEC_DEF`
  - `CIFSSEC_MAX`
  - `CIFSSEC_AUTH_MASK`

- Request/MID state constants:
  - `MID_*`
  - `CIFS_*_BUFFER`
  - send/receive request flags and operation types

## Global Declarations

When `DECLARE_GLOBALS_HERE` is defined, the header can switch declarations through `GLOBAL_EXTERN`, but this file primarily declares globals initialized in `cifsfs.c`, including:

- TCP session list and lock
- XID counters and lock
- allocation/reconnect/debug counters
- module option globals
- workqueues
- request/MID/netfs mempools
- dialect operation/value tables

## Locking Documentation

The header contains a detailed lock ordering table. It covers mount, volume context, superblock tlink trees, server reconnect/session locks, TCP session lock, tcon locks, inode locks, cached directory locks, file-info locks, RDMA locks, and MID locks. This is important because CIFS has nested server/session/tcon/inode/file state and many reconnect/oplock paths.

## Role in the Subsystem

`cifsglob.h` is the main structural contract for the CIFS client. Most implementation files include it either directly or indirectly, and the dialect-specific SMB1/SMB2/SMB3 implementations are bound to the common VFS/client layer through the operation table declared here.
