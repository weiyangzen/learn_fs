# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap.h

## Purpose

`xfs_bmap.h` declares the public block mapping interface used by XFS libxfs and higher-level filesystem code. It defines allocation state, bmapi flags, special startblock sentinels, extent update state flags, deferred bmap intent structures, validation helpers, and prototypes for mapping, unmapping, remapping, conversion, query, and extent-size hint operations.

## Main Types

### `struct xfs_bmalloca`

This is the central mutable allocation state passed through bmap allocation helpers. It carries:

- transaction and inode
- previous and current/next extent records
- requested logical offset and allocation length
- allocated filesystem block
- optional btree and in-core extent cursors
- allocation count and inode log flags
- total/minimum/minleft reservation constraints
- EOF, delayed-allocation, and conversion booleans
- allocation datatype
- bmapi flags

It ties allocation placement, extent insertion, btree updates, and accounting into one work object.

### `struct xfs_bmap_intent`

Represents a deferred bmap operation. It records the operation type, target fork, owner inode, optional group pointer, and the extent mapping to map or unmap later.

The intent types are:

- `XFS_BMAP_MAP`
- `XFS_BMAP_UNMAP`

## Important Flags

### `XFS_BMAPI_*`

These flags control mapping behavior:

- `ENTIRE`: return the whole extent rather than trimming to the request.
- `METADATA`: allocation is metadata rather than user data.
- `ATTRFORK`: operate on the attribute fork.
- `PREALLOC`: create or preserve unwritten preallocation.
- `CONTIG`: require a single contiguous allocation.
- `CONVERT`: convert extent state.
- `ZERO`: zero newly allocated or converted written extents.
- `REMAP`: map or unmap without normal allocation/free ownership semantics.
- `COWFORK`: operate on the CoW fork.
- `NODISCARD`: skip online discard for freed extents.
- `NORMAP`: skip rmap updates, used for reconstructing bmbt from rmapbt.
- `EXTSZALIGN`: try to align allocations to extent size hints.

### `BMAP_*`

These flags describe neighbor and fork state inside extent update state machines:

- left/right contiguity
- left/right filling
- left/right delayed allocation
- left/right validity
- attr fork
- CoW fork

## Special Startblocks

- `DELAYSTARTBLOCK` represents delayed allocation in returned mappings.
- `HOLESTARTBLOCK` represents holes in returned mappings.
- Null startblocks encode delayed allocation reservations internally.

The helper `xfs_bmap_is_real_extent` identifies allocated extents, and `xfs_bmap_is_written_extent` additionally excludes unwritten extents.

## Exported Operations

The header exposes:

- allocation accounting: `xfs_bmap_alloc_account`
- extent trimming: `xfs_trim_extent`
- fork conversion and attr fork setup
- btree max-level computation
- first/last logical extent queries
- read/write mapping: `xfs_bmapi_read`, `xfs_bmapi_write`
- unmapping: `xfs_bunmapi`, `xfs_bunmapi_range`
- delayed allocation and unwritten conversion helpers
- collapse/insert/split extent operations
- remapping: `xfs_bmapi_remap`
- deferred bmap intent helpers
- extent validation and corruption diagnostics
- bmap btree query helpers
- data and CoW extent size hint helpers

## Notable Invariants

- `xfs_bmapi_whichfork` gives precedence to `COWFORK`, then `ATTRFORK`, then data fork.
- `xfs_valid_startblock` rejects startblock zero for non-realtime inodes.
- `XFS_BMAP_MAX_NMAP` limits returned mappings to keep transactions bounded.
- Callers must combine flags carefully because `REMAP`, `PREALLOC`, `CONVERT`, `ZERO`, `NORMAP`, and `COWFORK` materially change quota, rmap, refcount, and data exposure semantics.

## Research Notes

This header is the contract for the whole XFS block mapping layer. Most correctness risk comes from flag combinations and from the shared `xfs_bmalloca` state object, which must remain consistent across allocation, extent insertion, btree conversion, and transaction logging.
