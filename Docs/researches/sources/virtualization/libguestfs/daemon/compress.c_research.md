# File Research: sources/virtualization/libguestfs/daemon/compress.c

Implements compressed FileOut streaming for files and devices.

Key points:
- Supports `compress`, `gzip`, `bzip2`, `xz`, and `lzop`, checking each external program exists before use.
- Validates compression levels according to tool-specific ranges.
- `do_compress_out` compresses a sysroot file; `do_compress_device_out` compresses raw device input using shell redirection.
- Streams command stdout to the client in `GUESTFS_MAX_CHUNK_SIZE` chunks.
- After sending the FileOut reply, subsequent read/pclose errors are reported by transfer cancellation.
