# File Research: sources/virtualization/libblockdev/src/plugins/fs/ntfs.c

Implements NTFS support through ntfs-3g/ntfsprogs utilities.

Key entry points:
- `bd_fs_ntfs_is_tech_avail()` checks utility dependencies.
- `bd_fs_ntfs_mkfs()` runs `mkntfs -f -F`.
- `bd_fs_ntfs_check()` runs `ntfsfix -n`.
- `bd_fs_ntfs_repair()` runs `ntfsfix -d`.
- `bd_fs_ntfs_set_label()` uses `ntfslabel`.
- `bd_fs_ntfs_set_uuid()` changes NTFS serial number through `ntfslabel`.
- `bd_fs_ntfs_get_info()` parses `ntfsinfo -m`.
- `bd_fs_ntfs_resize()` and `_get_min_size()` use `ntfsresize`.

Core mechanics:
- Dependencies are `mkntfs`, `ntfsfix`, `ntfsresize`, `ntfslabel`, and `ntfsinfo`.
- Mkfs options support label and dry run plus extra args.
- Check treats `ntfsfix` exit code 1 as “recoverable errors detected” without reporting an execution error.
- UUID validation accepts 8- or 16-character hexadecimal NTFS serial formats.
- `bd_fs_ntfs_set_uuid()` uses `--new-serial`, `--new-serial=<16 hex>`, or `--new-half-serial=<8 hex>`.
- Info queries reject mounted devices before running `ntfsinfo`.
- Info parsing extracts cluster size, volume size in clusters, and free clusters, then converts to bytes.
- Minimum-size parsing reads `You might resize at ... bytes` from `ntfsresize --info`.

Important invariants:
- NTFS labels are capped at 128 characters.
- NTFS info requires the device not to be mounted.
- Resize size is passed in bytes to `ntfsresize -s`.

Filesystem/block relevance:
- Adapts NTFS creation, basic consistency handling, serial/label management, size/free-space query, and resizing for block devices.

Notable risks:
- `ntfsfix` is not a full Windows chkdsk replacement; the API names it repair/check but behavior is utility-limited.
- Output parsing depends on `ntfsinfo` and `ntfsresize` English text.
- Mounted-device detection depends on libblockdev mount lookup.
