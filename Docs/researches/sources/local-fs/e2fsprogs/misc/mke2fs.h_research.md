# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.h

`mke2fs.h` is the shared local header between `mke2fs.c` and helper code such as `mk_hugefiles.c`.

Exports from `mke2fs.c`:
- `program_name`
- `quiet`
- `verbose`
- `zero_hugefile`
- `fs_types`
- `get_string_from_profile()`
- `get_int_from_profile()`
- `get_bool_from_profile()`

Exports from `mk_hugefiles.c`:
- `mk_hugefiles(ext2_filsys fs, const char *device_name)`

Research notes:
- The header intentionally exposes only the profile lookup and status globals needed by helper modules.
- `zero_hugefile` is shared so `mke2fs.c` can disable hugefile zeroing after discard/prezero detection.
