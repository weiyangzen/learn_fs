# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/fuse.h

Read completely: 515 lines.

This private/local FUSE protocol header defines Linux FUSE kernel protocol constants and wire structures used by perfuse. It sets protocol version 7.12, root node id, buffer sizing, xattr limits, flag constants, opcode enums, notify enums, and request/response structures for attributes, statfs, locks, lookup, getattr, mknod, mkdir, rename, link, setattr, open/create, release/flush, read/write, fsync, xattr, locking, access, init, CUSE init, interrupt, bmap, ioctl, poll, fallocate, directory entries, and invalidation notifications.

The header also defines compatibility structure sizes for older protocol forms and directory-entry alignment macros. Kernel-to-process and process-to-kernel header definitions are present under `#if 0` because equivalent definitions live in `perfuse.h`.

Security/reliability notes: this is ABI/wire-format-sensitive. Structure layout, integer widths, and alignment macros must match the Linux FUSE protocol expected by translated userspace filesystems.
