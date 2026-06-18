# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodisk.c

## Role

`gsiodisk.c` implements Ghostscript `%disk0%` through `%disk6%` IODevices as Adobe-style “flat disk” logical filesystems mapped onto host directories with a `map.txt` logical-name-to-number table.

This is Ghostscript virtual filesystem/IODevice code over the host filesystem; it is filesystem-adjacent but not a kernel filesystem.

## Main Interfaces

- Device definitions: `gs_iodev_disk0` through `gs_iodev_disk6`.
- IODevice operations: `iodev_diskn_init`, `iodev_diskn_fopen`, `diskn_delete`, `diskn_rename`, `diskn_status`, `diskn_enumerate_files_init`, `diskn_enumerate_next`, `diskn_enumerate_close`, `diskn_get_params`, `diskn_put_params`.
- Map-file helpers: `MapFileOpen`, `MapFileReadVersion`, `MapFileWriteVersion`, `MapFileRead`, `MapFileWrite`, `MapFileUnlink`, `MapFileRename`, `MapToFile`, `map_file_enum_init`, `map_file_enum_next`, `map_file_enum_close`, `map_file_name_get`, `map_file_name_del`, `map_file_name_add`, `map_file_name_ren`.

## Core Behavior

- Each `%diskN%` has a mutable `Root` parameter. Without a root, the device is unmounted/unsearchable/unwriteable and opens fail with `undefinedfilename`.
- Logical names are stored in `map.txt`; physical files are named by integer IDs in the root directory.
- Opening a logical file maps it to a physical numbered file. If missing and opened for write, the map entry is created first.
- Delete removes the map entry and unlinks the physical file. Rename updates map entries and deletes any destination logical file first.
- Enumeration scans `map.txt`, optionally matching logical names with `string_match`, and returns logical names rather than physical numbered names.
- Map updates are done by writing `Tmp.txt`, copying/editing entries, unlinking `map.txt`, and renaming the temp file.
- Device parameters report fake portable capacity values and expose the current `Root` string or null.

## Notable Risks

- The map file is plain text and update operations are not atomic with locking; concurrent writers can corrupt or lose entries.
- Map update helpers ignore many filesystem errors, including failed `unlink`/`rename` in helper routines.
- `diskn_rename` updates only the map entry and deletes any destination file; it does not rename the underlying numbered physical file, which is correct for the design but non-obvious.
- `diskn_put_params` allocates `gp_file_name_sizeof` bytes but stores `root_size = rootstr.size + 1`, so later capacity checks do not reflect the actual allocated buffer size.
- `map_file_enum_init` can return `NULL` after allocating `mapfileenum->root` if `root_name` is too long, without closing/freeing the partial enum.
- Logical names cannot include NUL, CR, or LF. Other path semantics are flattened into map entries rather than directories.
