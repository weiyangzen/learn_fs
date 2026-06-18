# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsfs.c

Read status: complete.

## Purpose

Provides the CIFS/SMB client’s Linux VFS and module integration: filesystem registration, superblock setup, mount flow, inode/file operation tables, module parameters, cache/mempool/workqueue initialization, and module teardown.

## Main Responsibilities

- Defines global module knobs for dialect security, buffer sizing, directory cache timeout, oplocks, signing, encryption strength, and request concurrency.
- Registers the `cifs` and `smb3` filesystem types.
- Builds and tears down CIFS superblocks.
- Implements VFS super operations, inode operation tables, and file operation tables.
- Initializes inode caches, SMB request buffers, MID pools, netfs I/O pools, workqueues, DFS/SPNEGO/SWN/idmap subsystems, and procfs integration.
- Implements server-side copy/remap helpers and file lease behavior.

## Important Areas

### Module and Global State

- Exposes module parameters:
  - `CIFSMaxBufSize`
  - `cifs_min_rcv`
  - `cifs_min_small`
  - `cifs_max_pending`
  - `dir_cache_timeout`
  - `enable_oplocks`
  - `enable_gcm_256`
  - `require_gcm_256`
  - `enable_negotiate_signing`
  - `disable_legacy_dialects`
- Defines global counters and locks:
  - XID counters under `GlobalMid_Lock`
  - allocation/reconnect counters
  - TCP session list and lock
  - request and MID allocation counters

### Superblock Lifecycle

- `cifs_sb_active()` / `cifs_sb_deactive()`
  - Maintain active references from CIFS superblock state to VFS superblock lifetime.

- `cifs_read_super()`
  - Configures POSIX ACL flag, read-only snapshot state, max file size, time granularity/range, xattr handlers, readahead, block size, root inode, dentry ops, and optional export ops.

- `cifs_kill_sb()`
  - Closes cached directories and deferred files, flushes oplock/deferred-close workqueues, drops root dentry, kills the anonymous superblock, and unmounts CIFS state.

- `cifs_umount_begin()` / `cifs_freeze()`
  - Wake blocked request waiters on forced unmount paths and close deferred files during freeze.

### Mount Flow

- `cifs_smb3_do_mount()`
  - Duplicates mount context, sets up `cifs_sb_info`, performs CIFS mount, reuses or creates a superblock via `sget()`, reads the superblock, and resolves root/prefix dentry.
  - Sets `SB_NODIRATIME | SB_NOATIME`.

- `cifs_get_root()`
  - Walks the prefix path from the share root when the mount uses a subpath.

### VFS Operations

- `cifs_super_ops`
  - Supplies `statfs`, inode allocation/free/drop/evict, writeback, mount option display, unmount-begin, and freeze hooks.

- Inode operation tables:
  - `cifs_dir_inode_ops`
  - `cifs_file_inode_ops`
  - `cifs_symlink_inode_ops`

- File operation tables:
  - `cifs_file_ops`
  - `cifs_file_strict_ops`
  - `cifs_file_direct_ops`
  - no-byte-range-lock variants
  - `cifs_dir_ops`

- `cifs_permission()`
  - Supports `noperm` behavior while still rejecting execute when execute bits are not present.

- `cifs_llseek()`
  - Revalidates file size for non-trivial seeks and delegates dialect-specific seek when available.

- `cifs_setlease()`
  - Allows local leases only when compatible with oplock/cache state or `local_lease`.

### Copy and Remap

- `cifs_remap_file_range()`
  - Implements clone/remap through server `duplicate_extents` when available.
  - Flushes source, adjusts source EOF if needed, flushes/invalidate destination pages, updates netfs/fscache size state, and maps some unsupported overlap cases to `-EINVAL`.

- `cifs_file_copychunk_range()` and `cifs_copy_file_range()`
  - Use server-side copychunk when possible, falling back to splice copy for unsupported or cross-device cases.
  - Maintains pagecache, fscache, inode size, and zero-point state.

### Initialization and Teardown

- `init_cifs()`
  - Initializes error maps, procfs, global counters, workqueues, inode/netfs/MID/request pools, DFS, SPNEGO, SWN, idmap, and filesystem registrations.
  - Uses structured unwind labels for partial initialization failure.

- `exit_cifs()`
  - Unregisters filesystems and tears down automount, idmap, optional upcall subsystems, pools, caches, workqueues, and procfs.

## Dependencies

- Includes CIFS global state, protocol prototypes, SMB2 prototypes, mount context, DFS/SWN/fscache/cached-dir support.
- Connects lower SMB dialect operations into Linux VFS objects.

## Notable Behaviors

- Snapshot mounts are forced read-only.
- Old SMB1-style servers get one-second timestamp granularity; modern SMB uses 100ns granularity.
- `/proc/mounts` option display is extensive and includes negotiated/cache/security/reparse/symlink/channel details.
- Workqueue and pool initialization order is mirrored carefully in failure unwind and module exit.
