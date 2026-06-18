# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_balloc.c

Read completely: 729 lines.

Implements LFS logical block allocation/accounting, fragment extension, indirect-block materialization, and write-pending block tracking for UVM page-backed writes.

Block allocation model:
- Missing blocks are represented as `UNASSIGNED`.
- Blocks accounted to the file but not yet written to disk are represented as `UNWRITTEN`.
- `lfs_balloc()` reserves free fragments before changing inode or indirect block pointers so ENOSPC can be reported before partial allocation.
- Effective block counts (`i_lfs_effnblks`) and superblock free counts are updated for newly accounted data and indirect blocks.

Main allocation behavior:
- Handles writes past EOF by extending a final fragment into a full block when necessary.
- Handles direct final-block fragment allocation or extension when writing within the direct block range.
- Uses `ulfs_bmaparray()` to discover existing mappings and required indirect path entries.
- Creates missing indirect blocks with cleared buffers and `UNWRITTEN` pointers.
- Reads existing indirect blocks if they are not already delayed-write or done.
- Marks direct, single-indirect, or deeper indirect references as `UNWRITTEN` for newly allocated blocks.
- If a caller asks for a buffer, returns an initialized/read buffer as needed; if writing a full block, may avoid an unnecessary read.

Fragment extension:
- `lfs_fragextend()` checks free space and quotas, optionally reads the old fragment buffer, waits for cleaner space if delayed-write accounting would exceed availability, grows the buffer, updates locked-buffer byte accounting, zeros newly added bytes, and updates inode/filesystem block accounting.

Write-pending page tracking:
- Defines an SPLAY tree keyed by logical block number for regular-file blocks dirtied through UVM without buffer headers.
- `lfs_register_block()` records a pending logical block, increases fake availability/page/locked-queue accounting, and waits for cleaner space first.
- `lfs_deregister_block()` removes one pending block unless a cleaner segment write is active.
- `lfs_deregister_all()` clears all pending entries for a vnode.

Risks and notes:
- Comments flag uncertain locking and questionable indirect-block cases, especially around single indirect handling and buffer initialization.
- Several code paths panic on unexpected indirect read failures.
- Correct accounting depends on matching register/deregister calls for page-backed writes and careful preservation of `UNWRITTEN` sentinel sign extension.
