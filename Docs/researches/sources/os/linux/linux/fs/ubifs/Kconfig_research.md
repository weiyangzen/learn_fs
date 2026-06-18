# File Research: sources/os/linux/linux/fs/ubifs/Kconfig

Purpose: Kconfig options for UBIFS.

Key options:
- `UBIFS_FS`: tristate UBIFS support, depends on `MTD_UBI`, selects CRC/hash/encryption-related helpers as needed.
- `UBIFS_FS_ADVANCED_COMPR`: exposes compressor choices.
- `UBIFS_FS_LZO`, `UBIFS_FS_ZLIB`, `UBIFS_FS_ZSTD`: compressor support, default `y`.
- `UBIFS_ATIME_SUPPORT`: optional atime updates, default `n` due to flash wear.
- `UBIFS_FS_XATTR`: extended attributes, default `y`.
- `UBIFS_FS_SECURITY`: LSM security labels, depends on xattrs, default `y`.
- `UBIFS_FS_AUTHENTICATION`: authentication support, selects `KEYS`, `CRYPTO_HMAC`, and `SYSTEM_DATA_VERIFICATION`.

Notes:
- Authentication help text warns that hash algorithms such as sha256 are not auto-selected.
