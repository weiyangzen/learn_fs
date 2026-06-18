# File Research: sources/os/linux/linux/fs/xfs/scrub/parent_repair.c

## Role
Repairs directory parent metadata. Without parent pointers it repairs `..`; with parent pointers it rebuilds the target inode’s parent-pointer xattrs from live directory entries using a temporary file and atomic attr-fork exchange.

## Setup
- `xrep_setup_parent` enables dirent fsgates, allocates `struct xrep_parent`, creates a repair tempfile, and tries to attach the orphanage.
- Parent-pointer repair requires rmapbt and exchange-range support.

## Legacy Repair
- `xrep_parent_find_dotdot` avoids sick directories, tries self-reference and dcache parent discovery, then scans the filesystem if needed.
- `xrep_parent_reset_dotdot` replaces the target directory’s `..` entry with the discovered parent inode.

## Parent-Pointer Rebuild
- `xrep_parent_scan_dirtree` scans all directories for dirents pointing to the scrub target.
- `xrep_parent_scan_dirent` converts each matching dirent into a stashed parent-pointer add operation.
- `xrep_parent_live_update` captures concurrent dirent adds/removes that affect already scanned directories.
- Stashed parent-pointer operations are periodically replayed into the tempfile to cap memory use.

## Xattr Preservation
- Non-parent xattrs are copied from the target inode into the tempfile.
- Large/remote xattr values are fetched as needed.
- If parent-pointer updates occur while opportunistically flushing copied attrs, the copy restarts with stronger locking.

## Commit Path
- `xrep_parent_finalize_tempfile` replays all pending pptr updates, ensures both inodes have attr forks, allocates exchange transaction resources, and locks both files.
- `xrep_parent_rebuild_pptrs` swaps the rebuilt attr fork into the target and resets the tempfile fork.
- Files with no parent can be moved to the orphanage; metadir superblock-rooted children are exempt.
- For non-directories, `xrep_parent_set_nondir_nlink` resets link counts and unlinked-list membership from rebuilt parent pointers.

## Risk Points
- Repair intentionally drops locks during full filesystem scans and relies on hooks for correctness.
- The pptr replay loop must finish with no queued updates before attr-fork exchange.
- If adoption cannot be performed for an otherwise parentless linked file, repair reports corruption.
