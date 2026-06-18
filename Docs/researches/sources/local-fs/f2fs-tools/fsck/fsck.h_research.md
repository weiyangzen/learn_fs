# File Research: sources/local-fs/f2fs-tools/fsck/fsck.h

## Purpose
Primary public header for fsck/dump/defrag/sload/resize shared declarations.

## Key constants/enums
- Fsck exit/status bits:
  - corrected errors
  - reboot required
  - uncorrected errors
  - operational error
  - usage error
  - user cancelled
  - shared library error
- Fsck inode/extent flags:
  - `FSCK_UNMATCHED_EXTENT`
  - `FSCK_INLINE_INODE`
- Preen modes:
  - `PREEN_MODE_0`
  - `PREEN_MODE_1`
  - `PREEN_MODE_2`
- Superblock copy identifiers:
  - `SB0_ADDR`
  - `SB1_ADDR`

## Key structures
- `struct orphan_info`: orphan inode list.
- `struct extent_info`: compact extent tuple.
- `struct child_info`: traversal state for directory/inode recursion, parent relationship, dot/dotdot counts, extent tracking, directory level, and name length.
- `struct f2fs_dentry`: linked stack used for dentry tree printing/file map output.
- `struct f2fs_fsck`: fsck runtime state, including:
  - embedded `f2fs_sb_info`
  - orphan state
  - check counters
  - hard-link tracking
  - main/NAT/SIT bitmaps
  - NAT entry cache
  - dentry traversal state
  - quota context
- `struct hard_link_node`: tracks expected vs actual links.
- `struct dump_option`: CLI/options for dump mode.

## Function declarations
Declares cross-module APIs for:
- fsck checking and verification
- metadata bitmap construction/rewrite
- NAT/SIT/SSA access and update
- current segment and checkpoint updates
- dump commands
- defrag, resize, sload
- file/directory creation
- xattr read/write
- node update
- journal flushing
- command-line helper `is_digits`

## Dependencies
Includes `f2fs.h`, so it also brings in raw F2FS disk definitions and fsck-local metadata structures.

## Research notes
This header is the central coupling point for the fsck tools directory. It exposes many implementation-level helpers across modules, which explains why `fsck.c`, `dir.c`, `dump.c`, `defrag.c`, and segment/mount code are tightly linked.
