# File Research: sources/virtualization/libguestfs/daemon/find.c

Implements `do_find0`, a FileOut API returning NUL-separated `find` results.

Important behavior:
- Validates the sysroot-expanded target exists and is a directory.
- Builds a quoted `find <sysrootdir> -print0` shell command.
- Sends the normal reply before streaming results via `send_file_write`.
- Strips the sysroot directory prefix from returned paths.
- Uses `input_to_nul` with `GUESTFS_MAX_CHUNK_SIZE`; overlong path chunks are rejected.

Filesystem relevance: streams recursive directory enumeration from the appliance without materializing the whole result in the protocol reply.
