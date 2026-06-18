# File Research: sources/virtualization/libguestfs/daemon/checksum.c

Implements checksum APIs for files, devices, and directory trees.

Key points:
- Maps checksum names to external programs: `cksum`, `md5sum`, `sha*sum`, `gostsum`, `gost12sum`.
- `checksum` streams an already-open fd to the program using `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN`.
- `do_checksum` opens a sysroot file inside chroot; `do_checksum_device` opens a raw device.
- `do_checksums_out` validates the path is a directory, then streams `find -type f -print0 | xargs -0 <sum-program>` from that sysroot directory.
- Uses pulse-mode progress for potentially long single-file/device checksum work.
