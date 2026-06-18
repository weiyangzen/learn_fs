# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/write.c

File data, directory records, dump directories, and descriptor terminator writer for ISO images.

Key behavior:
- `writefiles` recursively writes non-directory file contents, computes MD5 while copying, and reuses existing extents when `lookupmd5` finds duplicate content.
- `writedirs` writes directory trees from leaves upward, first sizing entries then writing, padding blocks, and patching `.`/`..` records.
- `writedumpdirs` writes the special dump hierarchy while preserving already-written day roots.
- `Cputplan9` emits Plan 9 system-use fields for bad original name, uid, gid, and mode.
- `genputdir` writes ISO/Joliet directory entries, including file flags, extent, length, date, identifier, and optional Plan 9 or Rock Ridge system-use data.
- `Cputisodir` and `Cputjolietdir` specialize `genputdir`.
- `Cputendvd` writes the volume descriptor set terminator.

Notable dependencies:
- MD5 from `libsec`.
- `Cputsysuse`, `Cputrscvt`, block I/O helpers, and dump dedup structures.

Research notes:
- Zero-length files get block 0; non-empty regular files assert block >= 18 when directory records are written.
- File copy updates length if the source changes during read and warns about it.
