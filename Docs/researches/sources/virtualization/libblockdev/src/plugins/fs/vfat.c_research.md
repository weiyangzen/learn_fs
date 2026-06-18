# File Research: sources/virtualization/libblockdev/src/plugins/fs/vfat.c

Implements VFAT/FAT filesystem support through dosfstools-style utilities.

Key entry points:
- `bd_fs_vfat_is_tech_avail()` checks required utilities and versioned UUID support.
- `bd_fs_vfat_mkfs()` runs `mkfs.vfat`.
- `bd_fs_vfat_check()` runs `fsck.vfat -n`.
- `bd_fs_vfat_repair()` runs `fsck.vfat -a`.
- `bd_fs_vfat_set_label()` and `_set_uuid()` use `fatlabel`.
- `bd_fs_vfat_get_info()` parses `fsck.vfat -nv`.
- `bd_fs_vfat_resize()` runs `vfat-resize`.

Core mechanics:
- Dependencies include `mkfs.vfat`, `fatlabel`, `fsck.vfat`, `vfat-resize`, and `fatlabel >= 4.2` for UUID setting.
- `_fix_uuid()` accepts udev-style volume IDs like `2E24-EC82` and converts them to 8 hex digits.
- Mkfs options uppercase labels, support volume ID, force, optional `--mbr=no` for newer `mkfs.vfat`, and extra args.
- Label setting uppercases non-empty labels and uses `--reset` for empty labels with newer fatlabel.
- Check treats exit code 1 as recoverable filesystem errors rather than command failure.
- Repair reruns fsck after exit code 1 to verify the filesystem is clean after correction.
- Info parsing extracts bytes per cluster and used/total cluster counts from fsck output, then computes free clusters.
- Resize passes an optional byte size to `vfat-resize`.

Important invariants:
- VFAT labels are at most 11 characters and must not contain `"*/:<>?\\|`.
- VFAT UUID/volume ID must fit in 32 bits and may be `NULL` for reset/random behavior depending on operation.
- FAT labels are normalized to uppercase by mkfs/set-label helpers.
- Generic feature metadata marks VFAT as partition-table-oriented and supports offline grow/shrink.

Filesystem/block relevance:
- Provides FAT-family creation, checking, repair, label/volume-ID management, size/free-space query, and resize behavior for block devices.

Notable risks:
- Info parsing assumes specific `fsck.vfat -nv` output formatting and device-prefix lines.
- Version-gated behavior around FAT partition tables and UUID changes depends on dosfstools output parsing.
