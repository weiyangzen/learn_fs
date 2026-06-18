# File Research: sources/os/linux/linux/fs/9p/vfs_inode.c

Implements inode and inode-operation handling for legacy 9P2000 and 9P2000.u.

Key behavior:
- Converts between Unix modes and 9p mode bits:
  - `unixmode2p9mode()` maps directories, devices, sockets, FIFOs, suid/sgid/sticky when dotu extensions allow them.
  - `p9mode2unixmode()` maps 9p stat mode and extension strings back to Linux file type, permissions, and device numbers.
- `v9fs_uflags2omode()` maps Linux open flags to legacy 9p open modes.
- `v9fs_blank_wstat()` prepares a “do not change” wstat structure.
- Allocates/frees 9p inodes from `v9fs_inode_cache`, initializes netfs state, address-space ops, inode ops, and file ops based on file type and protocol.
- `v9fs_evict_inode()` waits for netfs I/O, truncates pages, clears writeback, releases FS-Cache cookies, and clears the inode.
- Inode cache lookup uses QID version/type/path matching and rejects mismatched file types.
- `v9fs_inode_from_fid()` stats a FID and instantiates or reuses an inode.
- Remove path:
  - Prefer dotl `unlinkat` when available.
  - Fall back to path-based `p9_client_remove()`.
  - Updates nlink counts, invalidates attributes, and releases dentry FIDs.
- Create path:
  - Clones parent FID, sends `fcreate`, walks back to an unopened FID, creates the inode, attaches the dentry FID, and returns the opened create FID.
- Lookup walks from the parent FID, creates cached or always-new inodes depending on cache mode, and uses `d_splice_alias()`.
- Atomic open preserves Plan 9 create-open atomicity by passing the opened create FID directly to the file.
- Rename:
  - Rejects nonzero Linux rename flags.
  - Uses dotl renameat/rename if available.
  - Legacy/u path only supports same-directory rename through `wstat.name`.
  - Uses `rename_sem`, updates link counts, invalidates affected attributes, and performs `d_move()`.
- Getattr:
  - Uses cached inode attributes for meta/loose cache.
  - Flushes dirty writeback data before stat in writeback mode.
  - Otherwise fetches server stat and refreshes inode.
- Setattr:
  - Builds wstat fields for mode, times, size, uid/gid where supported.
  - Flushes dirty data first.
  - Resizes page/netfs/FS-Cache state on size changes.
  - Invalidates inode attrs and marks inode dirty.
- Supports dotu symlink, hardlink, and special-file creation through extension strings.
- `v9fs_refresh_inode()` refetches legacy stat data, preserving size in loose cache mode.

Important interactions:
- Dotl-specific inode operations are in `vfs_inode_dotl.c`.
- This file provides shared helpers used by dotl code too, including `v9fs_vfs_lookup()`, remove, rename, and open flag conversion for non-dotl.
