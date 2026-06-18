# File Research: sources/os/bsd/netbsd-src/sys/sys/statvfs.h

Read completely: 184 lines.

This public VFS statistics header defines `struct statvfs`, mount flag aliases, kernel helpers, and userland statvfs APIs. The structure stores mount flags, block sizes, block/file counts and reservations, sync/async read/write counters, fs IDs, name max, owner, spare fields, filesystem type, mount point, source, and source label.

It maps `ST_*` flags onto `MNT_*` flags, including access controls, logging, extended attributes, export flags, locality/quota/root flags, and wait/nowait modes. Kernel code gets helpers to set/copy/stat filesystem info plus allocation macros. Userland gets versioned `getmntinfo`, `statvfs`, `fstatvfs`, `getvfsstat`, and NetBSD file-handle/statvfs1 variants.

Risks: path/source buffers are large fixed-size ABI fields. Mount flag aliases must remain synchronized with `sys/fstypes.h`.
