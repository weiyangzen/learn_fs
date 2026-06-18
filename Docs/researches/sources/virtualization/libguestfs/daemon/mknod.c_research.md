# File Research: sources/virtualization/libguestfs/daemon/mknod.c

Implements special file creation when `mknod` is available.

Important behavior:
- Optional under `HAVE_MKNOD`.
- `do_mknod` rejects negative modes and calls `mknod` under chroot.
- `do_mkfifo`, `do_mknod_b`, and `do_mknod_c` require mode to contain only permission bits, then OR in the file type.
- Uses `makedev(devmajor, devminor)` for block/char nodes.

Filesystem relevance: creates FIFOs and device nodes inside guest filesystems.
