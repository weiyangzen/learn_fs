# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/openfs.c

Central filesystem-open path for libext2fs. `ext2fs_open()` delegates to `ext2fs_open2()`, which allocates the filesystem handle, opens the I/O channel, reads the superblock, validates features and geometry, reads group descriptors, starts MMP, and prepares optional support state.

Validation covers superblock magic, revision, checksum type and checksum retry, incompatible and readonly-compatible feature support, journal-device permission, block/cluster log constraints, bigalloc requirements, inode size, 64-bit descriptor size, group count, descriptor count, and inode count consistency.

Descriptor reading handles normal and `meta_bg` layouts, backup superblock recovery adjustments, big-endian descriptor swapping, image-file headers, and journal devices with no group descriptors.

Additional behavior: honors fake-time environment variables, parses `?` suffix I/O options from device names, initializes checksum seed, starts MMP for write/exclusive opens unless skipped, creates shared-block SHA map when requested, and loads UTF-8 NLS tables for casefold filesystems.
