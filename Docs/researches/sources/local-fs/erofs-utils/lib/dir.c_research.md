# File Research: sources/local-fs/erofs-utils/lib/dir.c

## Purpose
Directory entry iteration, fsck validation, and nid-to-pathname lookup.

## Important Functions
- `erofs_validate_filename()`: rejects names containing `/`.
- `traverse_dirents()`: parses one directory block's dirents, validates name offsets/lengths/order/file types/special entries when fsck mode is enabled, and invokes callback.
- `erofs_iterate_dir()`: opens a directory inode as a vfile and iterates block by block.
- `erofs_get_pathname_iter()`: recursive callback to find a target nid.
- `erofs_get_pathname()`: returns `/` for root or recursively searches from root for a nid.

## Fsck Checks
- Dirent `nameoff` must be sane.
- Names must be nonempty, bounded by `EROFS_NAME_LEN`, and within block.
- In fsck mode names must be sorted.
- `.` and `..` entries must not be duplicated and must point to expected nids.
- Directory filenames may not contain `/`.

## Interactions
- Used heavily by `fsck/main.c`.
- Uses `erofs_iopen()` and `erofs_pread()` from `data.c`.

## Notes
Path lookup recursively descends entries typed as directory or unknown, then verifies inode mode when necessary.
