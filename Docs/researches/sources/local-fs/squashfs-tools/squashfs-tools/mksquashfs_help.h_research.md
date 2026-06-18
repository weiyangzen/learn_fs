# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_help.h

Header for the help subsystem. It computes string suffixes used in help text based on `XATTR_SUPPORT`, `XATTR_OS_SUPPORT`, `XATTR_DEFAULT`, and `SINGLE_READER_THREAD`.

Exports help APIs for both `mksquashfs` and `sqfstar`, plus `display_compressors()` and `print_compressor_options()`.

The header also defines local `TRUE`/`FALSE`; callers mostly use it for help functionality and compile-time display text, not core build logic.
