# File Research: sources/os/linux/linux-stable/fs/erofs/Kconfig

## Summary
Declares EROFS and its optional features.

## Main Contents
- Core `CONFIG_EROFS_FS`
- Debugging
- xattrs, POSIX ACLs, security labels
- File-backed image support
- Compression and algorithms: LZ4, LZMA, DEFLATE, Zstd
- Hardware decompression acceleration
- Deprecated fscache on-demand support
- Per-CPU decompression workers
- Experimental page-cache sharing

## Important Behavior
Core EROFS depends on block support and selects common infrastructure such as CRC32 and iomap. Feature options select algorithm libraries and cache/crypto dependencies as needed.

## Risks
Many behavior combinations are compile-time dependent, especially compression, file-backed mode, fscache mode, and inode/page-cache sharing.
