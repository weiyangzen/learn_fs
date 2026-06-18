# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/file.h

Defines the checker’s auxiliary file-attribute override interface, mainly for paths that should be dropped or undeleted during FAT repair.

Key elements:
- `FD_TYPE` models override actions: none, drop, undelete.
- `FDSC` stores an 8.3 fixed-name entry, its action type, first child, and sibling link.
- `fp_root` is the global root of the override descriptor tree.
- Declares conversion and lookup helpers: `file_name`, `file_cvt`, `file_add`, `file_cd`, `file_type`, `file_modify`, `file_unused`.

Dependencies:
- Uses `MSDOS_NAME` from `msdos_fs.h`.
- Used by directory scanning/checking code to resolve user-specified file operations against FAT directory entries.

Research notes:
- This is a pure interface header; behavior lives elsewhere in the checker.
- The model assumes fixed 8.3 names for matching, even when the checker also tracks VFAT long names separately.
