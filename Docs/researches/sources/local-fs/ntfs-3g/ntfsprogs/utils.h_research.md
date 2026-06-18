# File Research: sources/local-fs/ntfs-3g/ntfsprogs/utils.h

## Purpose

Public header for shared ntfsprogs utility functions implemented in `utils.c`. It exposes mount/device helpers, parsing helpers, metadata/bitmap inspection helpers, attribute search helpers, MFT scan context APIs, dump formatting flags, and Windows compatibility wrappers.

## Exposed Interfaces

- Diagnostic strings:
  - `ntfs_bugs`
  - `ntfs_gpl`
- General helpers:
  - `utils_set_locale()`
  - `utils_parse_size()`
  - `utils_parse_range()`
  - `utils_inode_get_name()`
  - `utils_attr_get_name()`
  - `utils_cluster_in_use()`
  - `utils_mftrec_in_use()`
  - `utils_is_metadata()`
  - `utils_dump_mem()`
- Attribute search:
  - `find_attribute()`
  - `find_first_attribute()`
- Device and volume:
  - `utils_valid_device()`
  - `utils_mount_volume()`
- MFT scanning:
  - `struct mft_search_ctx`
  - `mft_get_search_ctx()`
  - `mft_put_search_ctx()`
  - `mft_next_record()`
- Unicode compatibility:
  - `ntfs_mbstoucs_libntfscompat()`
- Inline attribute-name helper:
  - `ntfs_attr_get_name(ATTR_RECORD *attr)` returns the in-record name pointer based on `name_offset`.

## Important Constants

- `FEMR_*` flags describe MFT search criteria and match state:
  - in-use/not-in-use
  - file/dir
  - metadata/not-metadata
  - base-record/not-base-record
  - all records
- `DM_*` flags control `utils_dump_mem()` formatting:
  - ASCII divider visibility
  - indentation
  - red/green/blue/bold terminal styling
- `MAX_PATH` is defined to `1024` if missing.

## Windows-Specific Behavior

When `HAVE_WINDOWS_H` is defined:

- Declares `ntfs_utils_reformat()` and `ntfs_utils_unix_path()`.
- Defines macro wrappers around `ntfs_log_redirect`, `printf`, `fprintf`, and `vfprintf` to rewrite format strings before passing them to older Windows runtimes.
- `MAX_FMT` is `1536`, setting the scratch-buffer size for reformatted output.

## Dependencies

- Includes `config.h`, `types.h`, `layout.h`, and `volume.h`.
- Optionally includes `errno.h` and `stdarg.h`.

## Role in Source Tree

This is the ntfsprogs utility contract consumed by tools that need common NTFS parsing, inspection, and reporting behavior without duplicating libntfs-3g glue code.
