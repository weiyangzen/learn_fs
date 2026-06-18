# File Research: sources/local-fs/f2fs-tools/mkfs/f2fs_format_main.c

Implements `mkfs.f2fs` command-line parsing, defaults, overwrite checks, and top-level program flow.

Key responsibilities:
- `mkfs_usage()` prints all supported options.
- `f2fs_show_info()` reports tool version, debug level, extension list usage, label, trim status, Android defaults, and enabled major features.
- Android default handling in `add_default_options()`:
  - Enables debug level, force overwrite, 4 KiB wanted sector size, root owner `0:0`.
  - Disables NAT bits and linear lookup by default for Android.
  - Enables encryption, quota/project quota, extra attrs, verity, and write hints unless readonly mode short-circuits.
- Compile-time default feature gates can enable casefold and project-id support.
- `f2fs_parse_options()` parses options for block size, extra devices and aliases, extensions, defaults, write hints, large NAT bitmap, label, zoned mode, overprovision, feature list, fake checkpoint seed, root owner, sparse mode, sections/zones, trim, fixed timestamp, UUID, casefold encoding/flags, reserved sections, target sectors, and device path.
- Validates feature dependencies: project quota, inode checksum, flexible inline xattr, inode crtime, and compression all require `extra_attr`.
- Disables `packed_ssa` for 4 KiB blocks.
- Calls `check_block_struct_sizes()` after options are resolved.
- With blkid, detects existing filesystems or partition tables and requires `-f` before overwriting.
- `main()` initializes configuration, parses options, checks mounted/writable device state, probes device/F2FS info, enforces zoned-mode constraints, formats, finalizes, and reports success/failure.

Important dependencies:
- Uses `INIT_FEATURE_TABLE` / `parse_feature()` from `f2fs_fs.h`.
- Uses libblkid when available for overwrite protection.
- Calls `f2fs_format_device()` from `f2fs_format.c`.

Behavioral notes:
- Extra devices are parsed as `device[@alias_filename]`; alias filenames cannot contain `/`.
- Custom target sectors are rejected for multi-device format.
- Sparse mode disables trim.
- Zoned device formatting requires both zoned feature mode and trim.
