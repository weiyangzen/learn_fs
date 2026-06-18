# File Research: sources/virtualization/libblockdev/src/plugins/fs/common.h

## Role

`common.h` declares internal shared helpers for filesystem plugin modules.

## Public/Internal Surface

It defines `_C_LOCALE` as the C locale handle used for locale-stable error messages.

It declares:

- `synced_close()`
- `get_uuid_label()`
- `check_uuid()`
- dependency-cache reset functions for ext, xfs, vfat, ntfs, exfat, btrfs, udf, f2fs, and nilfs

## Dependencies

Includes GLib and blkid.

## Notable Risks

This header is internal to plugin implementation but has no `G_GNUC_INTERNAL` annotations on declarations; symbol visibility is controlled elsewhere by build/export settings and definitions.
