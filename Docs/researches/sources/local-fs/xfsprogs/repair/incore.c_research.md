# File Research: sources/local-fs/xfsprogs/repair/incore.c

## Role

`incore.c` implements repair’s in-memory block state maps for data AGs and rtgroups, plus the legacy realtime extent bitmap.

## Group Block Maps

Each AG or rtgroup has a `struct bmap`:

- Cacheline-aligned mutex.
- Btree root keyed by block offset.
- Values are pointers to static state integers.

The btree records state transitions rather than one entry per block, making large runs compact.

## State Updates

`set_bmap_ext` changes the state of a block range. It handles all boundary cases:

- Updating an entire existing extent.
- Splitting a range inside a larger extent.
- Merging with previous or next extents when states match.
- Inserting new transition points at start/end boundaries.

`get_bmap_ext` returns the state at a block and optionally the length of the same-state run up to a caller-provided maximum.

## Realtime Bitmap

For non-rtgroup filesystems, realtime extents use `rt_bmap`, a packed 4-bit-per-extent array. Helpers:

- `get_rtbmap`
- `set_rtbmap`
- `reset_rt_bmap`
- `init_rt_bmap`
- `free_rt_bmap`

`rtsb_init` marks the first realtime extent in use if a realtime superblock exists.

## Initialization and Reset

`reset_ag_bmaps` initializes each AG:

- AG header blocks as `XR_E_INUSE_FS`.
- Valid AG body as `XR_E_UNKNOWN`.
- Beyond-AG region as `XR_E_BAD_STATE`.

`reset_rtg_bmaps` initializes rtgroups:

- Realtime superblock area as filesystem metadata where applicable.
- Remaining valid rtgroup blocks as free.
- End sentinel as bad state.

`reset_bmaps` also marks an internal log as filesystem metadata.

`init_bmaps` allocates AG bmaps, rtgroup bmaps or legacy rt bitmap, and resets them. `free_bmaps` releases them.

## Concurrency

`lock_group` and `unlock_group` serialize access to a single AG or rtgroup map. Higher-level inode scanning locks the group while checking/updating ranges.
