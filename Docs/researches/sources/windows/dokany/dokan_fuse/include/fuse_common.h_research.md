# File Research: sources/windows/dokany/dokan_fuse/include/fuse_common.h

Common public FUSE definitions shared by high-level and low-level headers.

Key contents:
- Enforces inclusion through `fuse.h` or `fuse_lowlevel.h`.
- Defines FUSE version as 2.7.
- Enforces `_FILE_OFFSET_BITS=64` outside MSVC.
- Defines `fuse_file_info` with flags, direct I/O/cache bits, flush marker, file handle, and lock owner.
- Defines `fuse_conn_info` with protocol version, async read flag, max write, max readahead, and reserved fields.
- Declares mount/unmount, command-line parsing, daemonize, version, and signal handler APIs.
- Provides compatibility remaps for older FUSE API versions.

Role:
- Supplies stable libfuse 2 common ABI declarations used by the compatibility implementation.
