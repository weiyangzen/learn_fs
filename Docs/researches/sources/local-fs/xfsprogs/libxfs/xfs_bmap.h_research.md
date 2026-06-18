# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bmap.h

## Purpose

`xfs_bmap.h` declares the public block mapping interface used by `libxfs` and other XFS subsystems. It defines allocation argument state, bmapi flags, special extent startblock values, extent update state flags, deferred bmap intent structures, validation helpers, and prototypes for mapping, unmapping, remapping, conversion, and query operations.

## Main Types

### `struct xfs_bmalloca`

This is the central allocation work structure passed through bmap allocation helpers. It carries:

- transaction and inode
- previous and current/next extent records
- requested logical offset and length
- allocated block number
- optional btree cursor and incore extent cursor
- number of allocations performed
- inode logging flags
- total/minimum allocation constraints
- EOF and allocation-mode booleans
- allocation datatype
- bmapi flags

This structure ties allocation placement, extent insertion, accounting, and btree updates together.

### `struct xfs_bmap_intent`

Represents a deferred bmap operation. It records:

- intent list linkage
- map or unmap type
- target fork
- owning inode
- optional group pointer
- extent record to map or unmap

Deferred intents are consumed by `xfs_bmap_finish_one`.

## Flags

### `XFS_BMAPI_*`

These flags control read/write/remap/unmap behavior:

- `XFS_BMAPI_ENTIRE`: return entire extents instead of trimming.
- `XFS_BMAPI_METADATA`: map metadata rather than user data.
- `XFS_BMAPI_ATTRFORK`: operate on attr fork.
- `XFS_BMAPI_PREALLOC`: allocate unwritten preallocation.
- `XFS_BMAPI_CONTIG`: require a single contiguous extent.
- `XFS_BMAPI_CONVERT`: convert written/unwritten state.
- `XFS_BMAPI_ZERO`: zero allocated or converted data extents.
- `XFS_BMAPI_REMAP`: map/unmap without ordinary block/refcount/quota changes.
- `XFS_BMAPI_COWFORK`: operate on CoW fork.
- `XFS_BMAPI_NODISCARD`: skip online discard for freed extents.
- `XFS_BMAPI_NORMAP`: skip reverse map updates.
- `XFS_BMAPI_EXTSZALIGN`: try extent-size-hint alignment.

Inline helpers map between flags and fork identifiers:

- `xfs_bmapi_aflag`
- `xfs_bmapi_whichfork`

### Special Startblocks

- `DELAYSTARTBLOCK`: externally visible delayed allocation marker.
- `HOLESTARTBLOCK`: externally visible hole marker.

### `BMAP_*` State Flags

These describe neighboring extent state during add/delete/convert operations:

- left/right contiguity
- left/right fill of an old extent
- left/right delayed allocation
- left/right neighbor validity
- attribute fork
- CoW fork

They are used internally to drive merge/split case analysis.

## Inline Extent Predicates

- `xfs_bmap_is_real_extent`: true for allocated physical extents.
- `xfs_bmap_is_written_extent`: true for allocated non-unwritten extents.
- `xfs_valid_startblock`: rejects block zero except for realtime inodes.

## Public Operations

The header exposes:

- attribute fork creation and local-to-extent conversion
- maximum btree level computation
- first/last extent offset lookup
- mapping read and write
- unmap and unmap range
- delayed allocation and CoW deletion helpers
- collapse/insert range support
- split extent support
- delayed allocation conversion to iomap
- unwritten extent conversion
- min-left reservation calculation
- low-space allocation helper
- remap helper
- deferred map/unmap operations
- bmap btree query helper
- extent-size hint accessors

## Validation Interface

The header declares:

- `xfs_bmap_validate_extent_raw`
- `xfs_bmap_validate_extent`
- `xfs_bmap_complain_bad_rec`

These are used when reading btree records and when external code needs to validate mapping records.

## Research Notes

This header defines the control surface for XFS block mapping. The flags are especially important because many operations share the same underlying mutation machinery but differ sharply in accounting and side effects. `XFS_BMAPI_REMAP`, `XFS_BMAPI_COWFORK`, and `XFS_BMAPI_NORMAP` are the most semantically sensitive flags because they intentionally bypass or redirect normal ownership/accounting behavior.
