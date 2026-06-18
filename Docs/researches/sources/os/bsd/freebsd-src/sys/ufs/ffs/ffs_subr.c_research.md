# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_subr.c

## Role

Provides shared FFS/UFS support routines used both in-kernel and by userland filesystem tools. It focuses on superblock loading, validation, recovery, writing, metadata check hashes, old-format compatibility, fragment accounting, block bitmap operations, and cluster accounting.

## Main Responsibilities

- Verifies and updates UFS2 inode check hashes.
- Reads a superblock from standard or alternate locations.
- Loads cylinder group summary information into `fs->fs_si`.
- Validates superblock field consistency and rejects unsafe values.
- Handles old UFS1/UFS2 compatibility field normalization on read and write.
- Searches alternate superblocks and boot-zone recovery data when the primary superblock is unusable.
- Writes superblock and summary information through caller-provided I/O callbacks.
- Calculates superblock check hashes.
- Updates fragment summary counters.
- Tests, sets, and clears free-block bitmap state.
- Updates cluster summary information for contiguous free block runs.

## Kernel/Userland Boundary

The file is written for dual use:

- In kernel builds, it includes vnode, buffer, mount, quota, inode, and sysctl headers and uses typed kernel malloc wrappers.
- Outside the kernel, it includes libc headers and exposes compatible allocation wrappers for tools such as libufs/fsck/newfs-style code.

The `ffs_sbget()` / `ffs_sbput()` APIs receive caller-provided read/write callbacks, so the same validation and serialization logic works across kernel buffers and userland device access.

## Superblock Read Path

`ffs_sbget()`:

- Reads either a requested alternate superblock or searches the `SBLOCKSEARCH` locations.
- Calls `readsuper()` for each candidate.
- Optionally stops after the superblock if `UFS_NOCSUM` is set.
- Allocates and fills `struct fs_summary_info`.
- Reads the cylinder group summary table from `fs_csaddr`.
- Initializes `fs_maxcluster` and `fs_contigdirs` in the summary area.

`readsuper()`:

- Calls the supplied block read function.
- Rejects `FS_BAD_MAGIC`.
- Handles the UFS1 64K block-size ambiguity around the UFS2 superblock location.
- Runs old-filesystem compatibility normalization.
- Runs full or recovery-only validation.
- Clears unsupported metadata check-hash and filesystem flags.
- Verifies the superblock check hash unless flags allow hash failure.
- Records `fs_sblockactualloc`.

## Validation and Recovery

`validate_sblock()` performs dense structural checks on:

- Magic number and endian mismatch.
- Superblock location.
- Block, fragment, sector, and cylinder group sizing.
- Inode geometry.
- Summary table location and size.
- Free inode/directory counts.
- Old UFS1 rotational layout fields.
- Maximum file size.
- Contiguous allocation parameters.

It distinguishes hard failures from warnings through `FCHK`, `WCHK`, and `FCHK2`. `UFS_NOWARNFAIL` can allow non-critical values to be normalized rather than fatal.

`ffs_sbsearch()` implements escalating recovery:

1. Try the standard superblock quietly.
2. Try the standard superblock while ignoring check-hash failures.
3. Try to use enough standard-superblock data to locate alternates.
4. If that fails, read UFS2 recovery data from the boot area.
5. Scan alternate cylinder group superblocks.
6. As a last resort, accept a standard superblock with only non-critical errors.

## Compatibility Handling

`ffs_oldfscompat_read()` updates older filesystems into the in-memory layout expected by current code:

- Copies old UFS1 fields into widened modern fields.
- Initializes `fs_flags` and `fs_sblockloc` where old filesystems lack them.
- Bounds UFS1 maximum file size.
- Supplies default average file size and files-per-directory values.

`ffs_oldfscompat_write()` copies fields back for on-disk compatibility and corrects unexpected superblock locations.

`ffs_oldfscompat_inode_read()` handles old UFS1 signed/unsigned timestamp issues by clamping future-looking times to the current mount time and marking the inode modified when needed.

## Metadata Check Hashes

- `ffs_verify_dinode_ckhash()` checks a UFS2 dinode CRC32C, excluding `di_ckhash` itself.
- `ffs_update_dinode_ckhash()` recomputes that field after inode changes.
- `ffs_calc_sbhash()` computes the superblock CRC32C, but returns the existing hash unchanged when superblock hashing is disabled.
- `readsuper()` disables metadata hashes if the filesystem was touched by a kernel that did not maintain them.

## Allocation Bitmap Helpers

`ffs_fragacct()` updates fragment availability summaries using the `fragtbl`, `around`, and `inside` tables from `ffs_tables.c`.

Block bitmap helpers are specialized by `fs_frag`:

- `ffs_isblock()` tests whether a full block is allocated/available in a fragment bitmap.
- `ffs_isfreeblock()` tests whether a full block is free.
- `ffs_clrblock()` clears a full block from the bitmap.
- `ffs_setblock()` sets a full block in the bitmap.

These helpers encode the historical FFS fragment layout for fragment counts 1, 2, 4, and 8.

## Cluster Accounting

`ffs_clusteracct()` maintains contiguous free-cluster summaries:

- Updates the cluster-free bitmap for an allocation or free.
- Scans forward and backward from the changed block.
- Adjusts the cluster length summary counts.
- Updates `fs->fs_maxcluster[cg]` to the largest available cluster in a cylinder group.

This supports FFS clustered allocation and read/write planning.

## Research Relevance

This file is central for understanding FFS on-disk trust boundaries. It captures how FreeBSD validates legacy metadata, recovers from damaged superblocks, maintains compatibility across decades of UFS format evolution, and represents fragment/cluster allocation summaries that higher-level allocation code depends on.
