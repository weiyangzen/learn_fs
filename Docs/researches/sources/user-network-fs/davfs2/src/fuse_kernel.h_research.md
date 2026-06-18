<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/fuse_kernel.h -->
# Research: sources/user-network-fs/davfs2/src/fuse_kernel.h

Purpose: vendored FUSE 2.5.3 kernel ABI definitions for FUSE protocol version 7.5, trimmed to the structures/opcodes davfs2 uses.

Important APIs/types: fixed-width aliases `__u64`, `__u32`, `__s32`; constants `FUSE_KERNEL_VERSION`, `FUSE_KERNEL_MINOR_VERSION`, `FUSE_ROOT_ID`, device major/minor, `FUSE_MIN_READ_BUFFER`; structs for attributes, statfs, request/response headers, lookup/create/open/read/write/release/setattr/init/access payloads, and directory entries; opcode enum including lookup, getattr, setattr, mkdir, unlink, rename, open, read, write, statfs, release, fsync, init, opendir/readdir, access, create.

Control flow and integration: `dav_fuse.c` casts the shared I/O buffer to these structs and uses enum values to dispatch kernel requests. `kernel_interface.c` uses `FUSE_MIN_READ_BUFFER` to size the device buffer and mount `max_read`.

State and persistence: no state; defines wire layout. Padding is part of ABI correctness.

Dependencies: must match Linux/FreeBSD FUSE kernel expectations for protocol 7.5. It intentionally removes include guards and external includes from original upstream file, relying on including C files to provide integer types.

Risks: ABI drift with modern FUSE kernels can cause subtle protocol bugs. The local comment notes a 2025 read buffer increase to 64 KiB, so buffer expectations changed from the original. Manual struct definitions need alignment/padding care across 32/64-bit builds.

Test signals: mount/read/write/readdir tests on current Linux and FreeBSD FUSE, protocol init negotiation, static size/offset assertions if added, and comparison with kernel FUSE headers for used structs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/fuse_kernel.h -->
