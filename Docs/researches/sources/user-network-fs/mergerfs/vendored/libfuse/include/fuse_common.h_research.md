<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_common.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_common.h

Purpose: This header defines common FUSE public types and functions shared by high-level and low-level APIs. It enforces 64-bit `off_t`, declares file-info flags, capability bits, mount/daemon utilities, buffer structs, and signal handler helpers.

Important APIs and types: `fuse_file_info_t` stores open flags, bitfield behavior flags, file handle, passthrough backing ID, and lock owner. Capability macros map public `FUSE_CAP_*` bits onto negotiated kernel features. `fuse_mount`, `fuse_unmount`, `fuse_parse_cmdline`, `fuse_daemonize`, `fuse_version`, and `fuse_pollhandle_destroy` are C ABI entry points. `fuse_buf` plus buffer flag enums describe memory or fd-backed data transfers.

Control flow and state: mount helpers create and tear down `/dev/fuse` sessions; signal handlers store a global session until removed. Buffers are transient descriptors and do not own fd lifetimes by themselves.

Risks and test signals: `_FILE_OFFSET_BITS=64` is mandatory. Bitfield layout is ABI-sensitive across compilers, so this header should only be used with the expected toolchain/ABI. Tests should cover command-line parsing, foreground/debug options, mount/unmount cleanup, signal exit behavior, and file-info flag translation into `fuse_open_out`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_common.h -->
