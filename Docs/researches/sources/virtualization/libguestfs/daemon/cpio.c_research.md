# File Research: sources/virtualization/libguestfs/daemon/cpio.c

Implements cpio archive streaming from a guest directory.

Key points:
- `do_cpio_out` validates the sysroot path exists and is a directory.
- Optional format is limited to `newc` or `crc`; default is `newc`.
- Runs `cd <dir> && find -print0 | cpio -0 -o -H <format> --quiet`.
- Streams archive bytes as FileOut chunks.
- Uses transfer cancellation for errors after the FileOut reply.
