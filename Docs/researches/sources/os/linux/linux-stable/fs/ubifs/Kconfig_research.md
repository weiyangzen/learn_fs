# File Research: sources/os/linux/linux-stable/fs/ubifs/Kconfig

Purpose: Defines UBIFS filesystem configuration options.

Key responsibilities:
- Declares `CONFIG_UBIFS_FS` as a tristate filesystem depending on `MTD_UBI`.
- Selects CRC, compression, crypto hash info, encryption support, and xattr dependencies as needed.
- Provides advanced compression options for LZO, zlib, and Zstd.
- Defines optional atime support, disabled by default to reduce flash wear.
- Defines xattr and security label support.
- Defines authentication support, selecting keys, HMAC crypto, and system data verification.

Important interactions:
- UBIFS depends on UBI flash volumes.
- Compression selections affect ability to read existing compressed filesystems.
- Authentication requires users to also select a suitable hash algorithm.

Notable invariants and risks:
- Enabling atime can increase writes and flash wear.
- Removing compressor support can make existing UBIFS images unreadable.
