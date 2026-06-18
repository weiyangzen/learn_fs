# File Research: sources/os/linux/linux/fs/overlayfs/super.c

## Purpose

`super.c` implements overlayfs superblock operations, filesystem registration, inode cache management, dentry revalidation, mount setup, upper/work/index directory preparation, layer/fsid construction, xino setup, overlap detection, and root dentry creation.

## Main Responsibilities

- Register the `overlay` filesystem type and inode slab cache.
- Provide superblock operations for inode allocation/free/destruction, sync, statfs, option display, and teardown.
- Implement dentry operations including `d_real()`, strong revalidation, weak revalidation, and case-insensitive hashing/comparison when needed.
- Validate and clone upper, work, lower, and data-only layer mounts.
- Probe upper/work filesystem capabilities such as xattrs, `d_type`, `O_TMPFILE`, `RENAME_WHITEOUT`, and file handles.
- Create or clean the workdir and indexdir.
- Allocate unique fsids and pseudo devices for underlying filesystems.
- Configure xino and persistent UUID behavior.
- Detect overlapping layers and in-use upper/work/lower paths.
- Construct the root overlay inode and dentry.
- Choose export operations depending on NFS export and file-handle availability.

## Important Functions

- `ovl_d_real()` returns the real backing dentry for data or metadata users, including lazy lowerdata lookup for metacopy data.
- `ovl_revalidate_real()` and `ovl_dentry_revalidate_common()` forward revalidation to upper and lower real dentries.
- `ovl_alloc_inode()`, `ovl_destroy_inode()`, and `ovl_free_inode()` manage `struct ovl_inode` lifetime.
- `ovl_sync_fs()` syncs the upper filesystem unless volatile sync status allows skipping.
- `ovl_statfs()` delegates statfs to the real root path and adjusts overlay type/name length/fsid.
- `ovl_workdir_create()` creates or cleans `work`/`index` directories under workbasedir.
- `ovl_lower_dir()` checks lower namelen, stack depth, file-handle support, and xino implications.
- `ovl_get_upper()` validates and clones upperdir, sets traps, inherits `SB_NOSEC`, and applies in-use locking.
- `ovl_check_rename_whiteout()` probes `RENAME_WHITEOUT` support.
- `ovl_make_workdir()` creates workdir and probes upper/work features, applying feature fallbacks.
- `ovl_get_workdir()` enforces upper/work same-mount and separate-subtree constraints.
- `ovl_get_indexdir()` verifies upper root origin, creates/opens indexdir, verifies index ownership xattrs, and invokes index cleanup.
- `ovl_get_fsid()` assigns per-underlying-filesystem fsids and detects conflicting/null UUID risks.
- `ovl_get_layers()` clones lower mounts, marks them read-only/noatime, assigns fsids, and sets casefold encoding.
- `ovl_get_lowerstack()` validates lower/data layer counts and builds the root lower stack.
- `ovl_check_overlapping_layers()` detects overlap with traps and in-use markers.
- `ovl_get_root()` creates and initializes the root overlay inode/dentry.
- `ovl_fill_super_creds()` performs the main mount construction under overlay credentials.
- `ovl_fill_super()` verifies user namespace, prepares credentials, and calls the credentialed setup.

## Mount Setup Flow

`ovl_fill_super()` sets dentry operations, prepares creator credentials if absent, and runs `ovl_fill_super_creds()` under those credentials.

`ovl_fill_super_creds()` verifies parsed parameters, allocates layer and lowerdir arrays, initializes superblock basics, and configures xino defaults. If an upperdir is present, it validates upperdir, checks volatile upper writeback error state, prepares workdir, and uses the upper superblock stack depth/time granularity.

The lower stack is then validated and converted into cloned private mounts. If persistent UUID/fsid support is enabled, the upper root UUID xattr may be initialized. If indexing is enabled and the mount is writable, the indexdir is created and cleaned. Overlapping layers are checked before final feature fallbacks and export operation selection.

Finally the function installs superblock flags and xattr handlers, creates the root dentry with `ovl_get_root()`, and leaves `ofs` attached to `sb->s_fs_info`.

## Upper/Work Feature Fallbacks

`ovl_make_workdir()` probes required and optional upper/work capabilities. Missing xattr support disables or downgrades redirect, metacopy, index, UUID, and xino where needed. Missing `d_type`, `O_TMPFILE`, or `RENAME_WHITEOUT` is warned for local filesystems, but remote upper filesystems must satisfy stricter requirements. File-handle absence disables index if required and contributes to `nofh`.

Volatile mounts create `work/incompat/volatile/dirty` so future mounts can detect incompatible dirty volatile state.

## Layer And Identity Model

Layer index 0 is upper. Lower layers are cloned private mounts and forced read-only/noatime. Regular lower layers receive fsids tied to unique underlying superblocks. Data-only layers share a special null fsid after normal lower fsids and are excluded from the merged root lower stack.

`ovl_get_fsid()` rejects or marks bad UUID situations that would make origin file-handle decoding ambiguous. This can force fallback from xino/index/NFS export to safer modes.

## Root Initialization

`ovl_get_root()` creates a directory inode, chooses the root inode number/fsid from upper or top lower, marks root as a merge directory with whiteout support, sets connected and upperdata flags, detects xwhiteout markers on lower roots, initializes inode state, installs dentry revalidation flags, and takes an upper dentry reference.

## Risk Notes

- Mount setup intentionally falls back for some feature failures but aborts for unsafe combinations such as remote upper missing required features.
- In-use and trap checks protect against overlapping layers and concurrent upper/work reuse; disabling index weakens exclusive protection.
- UUID conflicts can break origin decoding, so the code disables dependent features when ambiguity is detected.
- `d_real(D_REAL_DATA)` can trigger lazy lowerdata lookup and warns if no real data dentry can be found.
- Workdir/indexdir cleanup occurs during mount and must avoid corrupting valid index state.
