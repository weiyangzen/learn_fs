# File Research: sources/local-fs/jfsutils/xpeek/inode.c

Implements display/modification of JFS disk inodes and inode address resolution through IAGs.

Main command:
- `inode(void)`: parses inode number and optional table selector (`a`, `s`, or fileset `0`), resolves the inode address with `find_inode`, reads it, swaps to CPU order, displays it, and writes back if modified.

Display/edit:
- `display_inode(struct dinode *)`: prints core inode fields including inode stamp/fileset/number/generation, inode extent PXD, size, block count, link count, uid/gid, mode, timestamps, ACL descriptor, EA descriptor, next index, and ACL type.
- `change_inode(struct dinode *)`: allows modifying 35 displayed fields except reserved ACL/EA fields.
- `mode_string(mode_t)`: returns a compact 4-character type/permission summary, such as directory/read/write/execute indicators.

Lookup:
- `find_inode(unsigned inum, unsigned which_table, int64_t *address)`:
  - Computes IAG number and inode extent number from inode number.
  - Calls `find_iag`.
  - Reads the IAG through raw `ujfs_rw_diskblocks`.
  - Endian-swaps the IAG.
  - Uses `inoext[extnum]` to compute the physical byte address of the inode.

Integration points:
- Depends on `find_iag` from `iag.c`, `xRead`/`xWrite`, `ujfs_rw_diskblocks`, global `l2bsize`, `bsize`, and `type_jfs`.
- `display_inode` is also used by `display.c`.

Notable behavior and risks:
- Editing inode fields has minimal validation; invalid mode, extent, size, or timestamp values can corrupt filesystem semantics.
- `mode_string` tests `mode & ISUID & ISGID`, which only reports both bits if the bitwise chain remains nonzero; this is a questionable idiom and may not mean “both set” as clearly as `(mode & ISUID) && (mode & ISGID)`.
- `find_inode` returns failure when the target inode extent length is zero but does not explain allocation state to the caller.
