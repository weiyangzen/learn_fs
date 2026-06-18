# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/nt_io.c

Implements a Windows NT-native libext2fs I/O manager. It exposes `nt_io_manager()` and supplies open, close, set block size, read block, write block, and flush operations.

The file declares NT native APIs directly, maps NT/DOS errors to errno-style values, normalizes device names from drive letters and Unix-like names, opens devices with retry and read-only fallback, and supports lock, unlock, dismount, mounted check, flush, and partition type update operations.

I/O uses raw `NtReadFile`/`NtWriteFile` at block-derived offsets and enforces 512-byte alignment with assertions. The private channel maintains a one-block cache used for reads and updated by writes.

Caveats: `ext2fs_check_if_mounted()` appears to use `*mount_flags &= ...` after initializing to zero, which means it never sets `EXT2_MF_MOUNTED`; this may be intentional dead/legacy code or a latent bug. The implementation is highly Windows/NT-specific and relies on SEH constructs.
