# File Research: sources/os/linux/linux-stable/fs/squashfs/Makefile

## Summary
Builds the Squashfs kernel module/object and conditionally includes read-path, decompressor-thread, xattr, and compression-wrapper sources.

## Main Responsibilities
- Always links core files: block I/O, caches, directory lookup/readdir, export support, file reads, fragments, ids, inodes, name lookup, superblock, symlinks, decompressor registry, and page actors.
- Adds either `file_cache.o` or `file_direct.o` depending on the configured file decompression path.
- Adds selected decompressor threading implementations.
- Adds xattr files and selected compression wrappers based on Kconfig.

## Risks
Several core declarations in `squashfs.h` are satisfied by exactly one conditional implementation. Build correctness depends on Kconfig selecting a compatible file read path and at least one decompressor threading mode.
