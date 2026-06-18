# File Research: sources/local-fs/dosfstools/src/mkfs.fat.c

Implements the `mkfs.fat` command: creates FAT12, FAT16, FAT32, and Atari/GEMDOS-style FAT filesystems on block devices or newly-created image files.

Key elements:
- Defines packed on-disk structures for FAT boot sectors, FAT32 extensions, volume info, and FAT32 FSINFO.
- Maintains formatter state in file-static globals: target path, geometry, FAT size, sector size, cluster size, reserved sectors, root directory size, bad-block state, generated boot sector, FAT image, root directory, and write buffers.
- Provides FAT manipulation helpers:
  - `set_FAT_byte`
  - `read_FAT_cluster`
  - `mark_FAT_cluster`
  - `mark_FAT_sector`
- Implements bad-block handling through `check_blocks`, `do_check`, `get_list_blocks`, and `process_bad_blocks`.
- Computes filesystem geometry and defaults in `establish_params`.
- Builds boot sector, FAT, root directory, FSINFO, and optional fake MBR in `setup_tables`.
- Writes reserved sectors, boot sector, FAT copies, FAT32 backup sectors, FSINFO, and root directory in `write_tables`.
- Parses all command-line behavior in `main`.

Important behavior:
- FAT type selection follows FAT cluster-count boundaries:
  - FAT12 max: `4084`
  - FAT16 min/max: `4087` to `65524`
  - FAT32 min/max: `65525` to `268435446`
- FAT32 can be explicitly forced below the suggested minimum, with a warning.
- Large filesystems auto-select FAT32 when the target is at least 512 MiB unless overridden.
- Alignment is enabled by default and aligns reserved areas, FATs, and root directory layout to cluster size where applicable; it is disabled for tiny filesystems at or below 8192 sectors.
- Atari mode changes boot-sector layout assumptions, serial placement, FAT-size defaults, sector-size tuning, and GEMDOS compatibility checks.
- FAT32 root directory is allocated as cluster 2 unless bad-block processing moves it to the next usable cluster.
- Volume labels are converted through `charconv` helpers, padded to 11 bytes, validated against FAT label rules, and mirrored into both boot-sector volume info and root directory label entry when present.
- Reproducibility support exists through `SOURCE_DATE_EPOCH` and `--invariant`, affecting creation time, volume ID, and generated MBR disk signature.
- `--mbr` can embed a fake MBR partition table into boot-code space so whole fixed disks are more recognizable by Windows.

Dependencies:
- Includes `version.h` for `VERSION` and `VERSION_DATE`.
- Includes `common.h` for shared utility functions such as fatal error reporting, Atari detection, mounted-device checks, and volume ID generation.
- Includes `msdos_fs.h` for FAT directory-entry layout and attribute constants.
- Includes `device_info.h` for target type, geometry, size, partition, sector-size, and child-device detection.
- Includes `charconv.h` for DOS codepage setup, label conversion, and label validation.
- Uses `endian_compat.h` for portable little-endian conversions.

Filesystem construction flow:
1. Parse environment and CLI options.
2. Open or create the target.
3. Collect target device information.
4. Apply safety checks against mounted devices and devices with partitions/mappings.
5. Establish CHS/media/root-directory defaults.
6. Compute FAT geometry and allocate in-memory FAT/root/FSINFO tables.
7. Optionally scan or import bad blocks and mark affected clusters.
8. Write all filesystem metadata to the target and `fsync`.

Research notes:
- This is the central formatter implementation for dosfstools, not a reusable library module.
- The code intentionally writes only metadata regions and leaves most data-area sectors untouched.
- Many calculations are in logical sectors but bad-block and block-count paths still use 1024-byte blocks and 512-byte hard sectors, so unit conversion is a major correctness concern.
- Safety checks are conservative by default: mounted targets and fixed disks with child mappings are rejected unless explicitly overridden.
- `malloc_entire_fat` is only enabled when bad-block marking requires random FAT updates; otherwise only the first FAT sector is materialized and the rest is written as blank sectors.
