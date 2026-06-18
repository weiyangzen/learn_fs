# File Research: sources/virtualization/libguestfs/daemon/readdir.c

Streams rich directory entries.

Important behavior:
- `do_internal_readdir` opens a directory under chroot.
- Encodes `guestfs_int_dirent` records into an XDR buffer up to `GUESTFS_MAX_CHUNK_SIZE`.
- Precomputes maximum encoded record size using a filled `struct dirent`.
- Sends OK reply before streaming and can only cancel after that.
- Uses `d_type` when available, mapping to file type characters; otherwise returns unknown.

Filesystem relevance: efficient structured directory entry enumeration for guest directories.
