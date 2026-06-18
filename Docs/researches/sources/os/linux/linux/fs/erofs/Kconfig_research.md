# File Research: sources/os/linux/linux/fs/erofs/Kconfig

Defines EROFS build-time feature options.

Key behavior:
- Adds `EROFS_FS`, depending on block devices and selecting CRC32 and iomap support.
- Optional features include debug checks, xattrs, POSIX ACLs, security labels, file-backed mounts, compression, LZMA, DEFLATE, Zstandard, hardware acceleration, deprecated fscache-on-demand reads, per-CPU decompression workers, high-priority workers, and page-cache sharing.
- Compression options select their corresponding decompressor libraries.
- File-backed EROFS is enabled by default.
- On-demand fscache support is documented as deprecated.

Important interactions:
- Feature flags control which object files are linked by the Makefile and which helpers compile as stubs in `internal.h`.
