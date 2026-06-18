# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_accessors.h

Read completely: 1569 lines.

Provides inline accessor and utility macros for LFS structures, hiding 32-bit vs 64-bit format differences, optional endian swapping, v1 compatibility, and kernel/userland/standalone build differences.

Build and byte-order model:
- `STRUCT_LFS` lets libsa and cleaner code reuse accessors with alternate LFS-like structures.
- Byte-swap macros are disabled for standalone and kernel builds without `LFS_EI`; otherwise they consult `lfs_dobyteswap`.
- `LFS_LITTLE_ENDIAN_ONDISK()` determines directory old-format interpretation.
- Compiler diagnostics are suppressed around packed-member address type checks used by accessor generators.

Directory and inode accessors:
- Defines directory record sizing (`LFS_DIRECTSIZ`, `LFS_DIRSIZ`, `LFS_MAXDIRENTRYSIZE`) and navigation (`LFS_NEXTDIR`).
- Inline functions get/set directory inode, record length, type, name length, name pointer, and directory-template dotdot fields.
- Handles old 32-bit directory format by returning `LFS_DT_UNKNOWN` and extracting namlen from the byte that overlaps `dh_type` on little-endian media.
- Dinode helpers copy only the active 32-bit or 64-bit structure and generate accessors for mode, nlink, inode number, size, times, flags, blocks, gen, uid/gid, and fake rdev.
- Direct and indirect block accessors preserve sign extension so sentinel values such as `UNWRITTEN` survive 32-bit reads.
- Birthtime is stored only for 64-bit dinodes.

Buffer, ifile, and segment metadata helpers:
- `LFS_LOCK_BUF` and `LFS_UNLOCK_BUF` maintain global locked-buffer count and byte accounting.
- `LFS_SET_UINO` and `LFS_CLR_UINO` maintain unwritten/dirty inode accounting for accessed/cleaning/modified state bits.
- `LFS_SEGENTRY`, `LFS_IENTRY`, `LFS_CLEANERINFO`, and related write macros read and dirty ifile-backed segment usage, inode, and cleaner blocks.
- Generated accessors cover FINFO, IINFO, IFILE, CLEANERINFO, SEGSUM, and superblock fields.
- Free-list head/tail helpers synchronize superblock fields and cleaner info fields for newer formats.
- Superblock accessors handle 64-bit, 32-bit, and 32-bit-only fields such as `ifile`, `segmask`, and `segshift`.

Addressing and free-space helpers:
- Defines block pointer/inode-number sizes, indirect count, inode-per-block/fragment helpers, fragment/block/disk address conversions, block rounding, LFS segment address conversions, and file block sizing.
- `union lfs_blocks` helpers provide format-independent pointer arithmetic over 32-bit or 64-bit block-pointer arrays.
- Free-space estimation macros account for dirty metadata, estimated clean metadata overhead, reserved minimum-free space, and privileged credentials.
- `LFS_NRESERVE` estimates minimum blocks needed to create a new inode.

Risks and notes:
- Many macros perform I/O, lock acquisition, dirty marking, and panics, so they are not simple field accessors.
- Correctness depends on callers holding the expected locks, especially ifile, fragment, segment, and global `lfs_lock` contexts.
- Several comments note file-ordering problems, disabled assertions, and old compatibility paths that should eventually be cleaned up.
