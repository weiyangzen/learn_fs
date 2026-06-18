# File Research: sources/virtualization/qemu/block/raw-format.c

Implements QEMU's `raw` format driver as a thin pass-through layer over a file child, with optional `offset` and fixed `size` bounds. Without offset/size it behaves like a filter; with either option it is a bounded data node whose logical offsets are translated into the containing file.

`raw_apply_options()` validates that the offset lies within the child size, that optional size fits and is sector-aligned, and records the effective virtual size. `raw_adjust_offset()` enforces bounds for reads/writes and adds the configured base offset. Read, write, write-zeroes, discard, block status, copy-range, truncate, getlength, get-info, ioctl, eject, lock-medium, zoned operations, zero-init, and cancel-in-flight mostly forward to the child after this translation.

A key safety feature handles probed raw images. If QEMU guessed raw format, writes to block 0 are restricted: the first 512 bytes are copied to an aligned buffer, reprobed, and rejected with `-EPERM` if they would make another format driver match. This prevents a guest from creating a format header that later changes interpretation of the image. Probed raw images also get 512-byte request alignment.

The driver supports mutable `offset` and `size` reopen options, raw image creation by creating the underlying file, measuring raw size, passing through block size/geometry probing where safe, and permission adjustment that avoids requesting child WRITE/RESIZE unless the parent actually needs them.
