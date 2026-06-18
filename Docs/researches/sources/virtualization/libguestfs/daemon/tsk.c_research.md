# File Research: sources/virtualization/libguestfs/daemon/tsk.c

## Role
Implements internal filesystem walking and inode search using The Sleuth Kit when libtsk support is available.

## Main Flow
- `do_internal_filesystem_walk()` opens the mountable’s device with TSK and recursively walks allocated and unallocated directory entries.
- `do_internal_find_inode()` performs the same walk but emits only entries whose metadata address matches the requested inode.
- `open_filesystem()` uses `tsk_img_open()` and `tsk_fs_open_img()` with type autodetection.
- Callbacks serialize `guestfs_int_tsk_dirent` records with XDR and stream them via FileOut.

## Metadata Extraction
- Maps TSK file name/meta types to compact type characters.
- Computes allocation, reallocation, and compression flags.
- Copies size, link count, atime, mtime, ctime, crtime, and symlink target when metadata exists.
- Skips `.` and `..` entries except the filesystem root entry.

## Feature Gate
When libtsk is unavailable, the file expands `OPTGROUP_LIBTSK_NOT_AVAILABLE`.

## Filesystem/Storage Relevance
This file enables forensic-style traversal of filesystems, including deleted/unallocated entries, without mounting them through the kernel.
