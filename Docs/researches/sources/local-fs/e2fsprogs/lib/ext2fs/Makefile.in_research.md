# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/Makefile.in

## Purpose
Autoconf makefile template for building, testing, installing, and cleaning `libext2fs` and related debug/test utilities.

## Main Elements
- Build variables: source/build roots, `my_dir`, install tools, debugfs-specific flags, generated tool commands `mk_cmds` and `compile_et`.
- Object lists:
  - Optional debugfs/resizer/e2image/test I/O/TDB objects.
  - Core `OBJS` for libext2fs, including allocation, bitmaps, block mapping, directory, extent, inode, journal, metadata checksum, I/O, undo, sparse, and rbtree modules.
  - `SRCS` mirrors the source files and generated/test sources.
- Library metadata: static, ELF shared, BSD library image/version/install settings.
- Compile rules: normal, static/profile/shared/PIC object generation plus static analysis hooks.
- Generated files: `ext2_err.et`, `ext2_err.c/.h`, `ext2fs.pc`, `ext2_types.h`, `crc32c_table.h`, `utf8data.h`.
- Test targets: build and run `tst_badblocks`, `tst_bitops`, `tst_icount`, `tst_bitmaps`, checksum/hash tests, inline-data tests, and `tst_libext2fs`.
- Install/uninstall/clean/distclean targets.
- Manually maintained dependency section for all lib objects and debugfs-linked utilities.

## Dependencies And Integration
Pulls in makefile fragments via `@MAKEFILE_LIBRARY@`, `@MAKEFILE_ELF@`, `@MAKEFILE_BSDLIB@`, and `@MAKEFILE_PROFILE@`. Bridges `lib/ext2fs`, `debugfs`, `e2fsck`, `misc`, `lib/support`, `lib/et`, `lib/ss`, e2p, uuid, blkid, archive, and OS-specific I/O.

## Risk Notes
The dependency block is explicitly manually maintained, including Windows I/O caveats. Any source/header addition must update both object/source lists and dependency rules or parallel/incremental builds can become stale. The debugfs build intentionally reaches into e2fsck journal recovery sources due to shared journal code.
