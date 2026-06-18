# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrefcount_btree.c

## Purpose

`xfs_rtrefcount_btree.c` implements the realtime reference count btree. This inode-rooted btree tracks shared/COW reference counts for extents on the realtime device and mirrors regular refcount btree behavior with realtime-group-specific roots and cursors.

## Main Content

- Defines a kmem cache for realtime refcount btree cursors.
- Implements btree cursor operations:
  - Cursor duplication.
  - Min/max records.
  - On-disk root max records.
  - Key and high-key initialization.
  - Record initialization from cursor state.
  - Key comparisons and contiguity.
  - Pointer initialization.
- Implements block verification:
  - Magic number validation.
  - Reflink feature validation.
  - V5 fsblock btree header validation.
  - Level and max-record checks.
  - CRC read/write verification.
- Defines `xfs_rtrefcountbt_buf_ops`.
- Defines `xfs_rtrefcountbt_ops` for inode-rooted btree operations.
- Allocates live cursors with RT group references and metadata inode state.
- Commits staged btree roots by replacing the real inode fork and logging inode core/root.
- Computes block max records, on-disk max levels, mount max levels, btree size, and reserve size.
- Converts btree roots between on-disk dinode fork format and in-memory btree block format.
- Loads and flushes realtime refcount metadata btree roots from/to metadata inodes.
- Creates an empty realtime refcount metadata inode root.

## Key Interfaces and Invariants

- Realtime refcount btrees require realtime reflink support; loading with only generic reflink is tolerated for growfs preparation, but corruption is reported if reflink is absent.
- The btree is inode-rooted and uses long pointers, but root packing differs between in-core and on-disk forms.
- Root pointer arrays are not immediately adjacent to the block header, so root reallocations must move pointer arrays explicitly.
- `m_rtrefc_maxlevels`, `m_rtrefc_mxr`, and `m_rtrefc_mnr` must be initialized from mount geometry before verification and reservations are meaningful.
- Reserve sizing assumes one refcount record per realtime extent in a group.
- Staged root commit transfers the staging fork by shallow copy after destroying the real fork.

## Dependencies

Depends on generic btree, btree staging, refcount record encoding, realtime groups, metadata inode allocation, health tracking, buffer CRC helpers, transactions, and inode fork conversion helpers.
