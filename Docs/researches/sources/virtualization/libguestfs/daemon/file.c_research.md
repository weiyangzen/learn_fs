# File Research: sources/virtualization/libguestfs/daemon/file.c

Implements core file mutation and byte-range I/O daemon actions: `touch`, `rm`, `rm_f`, `chmod`, `chown`, `lchown`, deprecated `write_file`, internal write helpers, `pread`/`pwrite` for files and devices, `zfile`, `filesize`, and `copy_attributes`.

Important behavior:
- Uses `CHROOT_IN/CHROOT_OUT` for guest filesystem paths, while device reads/writes operate directly on device paths.
- `do_touch` first `lstat`s and only permits regular files or non-existent paths, with an acknowledged TOCTOU caveat.
- `pread_fd` rejects negative count/offset and caps reads below `GUESTFS_MESSAGE_MAX`.
- `pwrite_fd` closes before optionally calling `udev_settle` for block-device writes.
- `do_zfile` builds a quoted shell pipeline `zcat|bzcat ... | file -bsL -`.
- `do_copy_attributes` optionally copies mode, ownership, and xattrs, with `all` expanding unspecified optional flags.

Filesystem relevance: this is the daemon’s generic local file/syscall bridge and its direct raw block-device byte I/O path.
