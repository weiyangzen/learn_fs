# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodisk.c

Implements `%disk0%` through `%disk6%` IODevices using flat OS directories plus a logical filename map.

Design:
- Each disk has a `/Root` parameter pointing at an OS directory.
- Logical filenames are mapped to numeric flat files through `map.txt`.
- This avoids OS filename/path restrictions and simulates Adobe’s flat disk structure.
- The number of disks is limited to seven due to DynaLab installer compatibility.

IODevice operations:
- `iodev_diskn_fopen`: maps logical name to real numeric file; creates a map entry on write.
- `diskn_delete`: removes map entry and unlinks real file.
- `diskn_rename`: removes destination if present and rewrites map name.
- `diskn_status`: maps logical name and stats real file.
- `diskn_get_params`/`diskn_put_params`: expose and update `Root`, mount/search/write flags, and fake capacity values.
- Enumeration delegates to map-file enumeration once Root is set.

Map file format:
- First line: `FileVersion\t1\t...`
- Remaining lines: numeric file id plus logical filename.
- `Tmp.txt` is used as a rewrite target for add/delete/rename operations.

Map helpers:
- `MapFileOpen`, read/write version, read/write entry, unlink/rename helpers.
- `MapToFile`
- `map_file_enum_init`, `map_file_enum_next`, `map_file_enum_close`
- `map_file_name_get`, add, delete, rename

Risks and quirks:
- Map rewrites are not atomic beyond rename patterns and have no locking.
- Several operations silently return if helper file operations fail.
- Root buffer allocation always uses `gp_file_name_sizeof`, while `root_size` is set to actual string size plus one.
- Logical names cannot include NUL, CR, or LF.
