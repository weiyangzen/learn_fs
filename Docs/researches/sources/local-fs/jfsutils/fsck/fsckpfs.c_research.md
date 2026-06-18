# File Research: sources/local-fs/jfsutils/fsck/fsckpfs.c

## Role

`fsckpfs.c` is the physical/persistence support layer for `fsck.jfs`. It centralizes low-level reading, writing, caching, flushing, endian swapping, and traversal for JFS fsck metadata structures.

The file bridges logical fsck operations to on-device data:

- Aggregate inode table nodes.
- Fsck workspace block map pages.
- JFS block allocation map pages.
- Directory dnodes.
- Extended attributes.
- Fsck in-aggregate log.
- Inode allocation groups and inode extents.
- Inode table control pages.
- XTree nodes.
- Device open/close and aligned read/write.
- Directory reconstruction buffers.

## Global State

The file uses:

- `sb_ptr` for filesystem block size and superblock metadata.
- `agg_recptr` for all fsck buffers, buffer offsets, dirty flags, selected AIT parts, map traversal state, and workspace dimensions.
- `Vol_Label` for diagnostics.
- `Dev_IOPort`, `Dev_blksize`, `Dev_SectorSize`, and `ondev_jlog_byte_offset` from device/global fsck state.

## Major Subsystems

### AIT and XTree Access

- `ait_node_get()` reads an AIT xTree node by aggregate block offset, rejects targets beyond the fsck workspace boundary, and swaps `xtpage_t` after read.
- `ait_node_put()` writes an AIT node after swapping to disk format and then swaps back.
- `ait_special_read_ext1()` reads the first extent of the primary or secondary Aggregate Inode Table into the inode buffer. It is used early before normal inode lookup infrastructure is fully available.

### Fsck Workspace Block Map

- `blkmap_find_bit()` maps an aggregate block number to fsck workspace bitmap page, byte offset, and bit mask.
- `blkmap_get_ctl_page()` reads the workspace block map control page.
- `blkmap_put_ctl_page()` writes the control page immediately because it carries serviceability state for interrupted fsck sessions.
- `blkmap_get_page()` pages workspace bitmap data into a shared buffer, flushing dirty data first.
- `blkmap_put_page()` marks the current workspace block map buffer dirty.
- `blkmap_flush()` writes dirty workspace block map pages back to disk.

### JFS Block Allocation Map

- `blktbl_ctl_page_put()` writes the JFS block map control page through the generic map-control buffer.
- `blktbl_dmap_get()` locates and reads a dmap page for a block by using the selected aggregate block map inode and xTree lookup.
- `blktbl_dmap_put()` marks the dmap buffer dirty.
- `blktbl_dmaps_flush()` writes dirty dmap data.
- `blktbl_Ln_page_get()` reads summary-level `dmapctl` pages.
- `blktbl_Ln_page_put()` marks summary-level pages dirty.
- `blktbl_Ln_pages_flush()` writes dirty summary-level pages.

### Directory Nodes and Reconstruction

- `dnode_get()` reads or reuses cached directory dnode pages, bounds-checking against the fsck workspace boundary and marking swapped pages with `BT_SWAPPED`.
- `recon_dnode_assign()` allocates a reconstruction buffer for a new dnode and records its target offset in a trailer record.
- `recon_dnode_get()` allocates and reads an existing dnode into a reconstruction buffer.
- `recon_dnode_put()` writes a reconstruction dnode and releases the buffer.
- `recon_dnode_release()` releases a reconstruction buffer without writing.

### Extended Attributes

- `ea_get()` reads EA data from a block offset into caller-provided storage and returns `FSCK_BADEADESCRIPTOR` if the read is short.

### Fsck Log

- `fscklog_put_buffer()` writes the current fsck log buffer into the in-aggregate fsck log when read/write and not full.
- Log write failures are recorded in the workspace control page but deliberately do not stop fsck processing.
- The routine advances log offsets and marks log full when another buffer will not fit.

### Inode Allocation Groups and Inode Traversal

- `iag_get()` reads a specific IAG by table ownership, table inode, selected AIT, and IAG number.
- `iag_get_first()` initializes sequential IAG traversal, handling both root-leaf inode maps and external imap leaves.
- `iag_get_next()` advances sequential IAG traversal across imap leaves.
- `iag_put()` marks the IAG buffer dirty.
- `iags_flush()` writes dirty IAG data.

### Inode Extent Access

- `inode_get()` returns an inode by choosing the proper AIT part, locating the relevant IAG, finding the inode extent descriptor, reading the inode extent, and endian-swapping it.
- `inode_get_first_fs()` initializes sequential fileset inode traversal, starting at `FILESET_OBJECT_I`.
- `inode_get_next()` advances within an inode extent, then across allocated extents and IAGs.
- `inode_put()` marks the inode buffer dirty.
- `inodes_flush()` writes dirty inode extents after swapping to disk format and swaps back.

### Inode Table Control Pages and Generic Map Control Pages

- `inotbl_get_ctl_page()` locates aggregate or fileset inode table control pages, using AIT fixed offsets or the fileset inode map tree.
- `inotbl_put_ctl_page()` swaps and writes inode table control pages through `mapctl_put()`.
- `mapctl_get()` reads or reuses a generic map-control page buffer.
- `mapctl_put()` marks the generic map-control page buffer dirty.
- `mapctl_flush()` writes dirty generic map-control data.

### Device Access

- `open_device_read()` opens the target device/file read-only and initializes block size globals to `PBSIZE`.
- `open_device_rw()` attempts exclusive read/write open, falls back to non-exclusive read/write for kernels that reject `O_EXCL` on read-only-mounted block devices, and initializes block sizes.
- `open_volume()` chooses read-only or read/write access from fsck options and falls back to read-only if read/write open fails.
- `close_volume()` flushes and closes the device.
- `readwrite_device()` enforces journal target protection, sector alignment, dispatches to `ujfs_rw_diskblocks()`, and reports actual byte count as all-or-nothing.

## Buffering and Write Policy

Most `_put()` functions do not write immediately. They mark the corresponding buffer dirty, and the next get/flush operation writes it. Immediate writes are reserved for metadata where interruption diagnostics matter or where the buffer is transient:

- Immediate: workspace block map control page, fsck log buffer, reconstruction dnode writes.
- Deferred: block map pages, dmaps, summary pages, IAGs, inode extents, generic map control pages.

The standard pattern is:

1. If requested data is already in the matching buffer range, return a pointer.
2. Before reading a different page/extent, flush dirty buffer state.
3. Read from disk into the buffer.
4. Endian-swap into host format.
5. Record buffer offsets, logical positions, lengths, and ownership metadata.
6. Mark dirty with a `_put()` routine if caller mutates data.

## Safety Checks

- `readwrite_device()` refuses targets at or beyond `ondev_jlog_byte_offset`, preventing fsck from accidentally overwriting the journal.
- Many readers reject offsets beyond `agg_recptr->ondev_wsp_fsblk_offset`, treating them as corrupt metadata targets rather than I/O errors.
- Device offset and requested length must be sector-aligned.
- Short reads/writes are converted into explicit `FSCK_FAILED_*` errors with user/debug messages.
- Dirty flushes swap structures to disk format, write, then swap back to preserve in-memory host format.

## Notable Observations

- `checksum(uint8_t *, uint32_t)` is prototyped but not defined or used in this file.
- `mapctl_flush()` writes `mapctl_buf_data_len` bytes but checks `bytes_written == mapctl_buf_length`; this may be correct when those are always equal for control pages, but it is a detail worth verifying.
- Several debug/error messages in `imapleaf_get()` reference `node_*` buffer fields rather than `mapleaf_*` fields, likely due to shared/copy-paste diagnostics.
- The code assumes `readwrite_device()` performs all-or-nothing byte counts because it sets `actual_data_size` to `requested_data_size` on success and `0` otherwise.
- Endian swapping is intentionally caller-aware for generic map control pages because the buffer may contain either `dbmap` or `dinomap`.

## External Dependencies

The file relies on definitions and helpers from `xfsckint.h`, `xchkdsk.h`, `jfs_byteorder.h`, `devices.h`, and `utilsubs.h`.

Key external helpers include:

- Disk I/O: `ujfs_rw_diskblocks()`, `ujfs_flush_dev()`, `fopen_excl()`.
- Tree lookup: `xTree_search()`.
- Buffer allocation: `dire_buffer_alloc()`, `dire_buffer_release()`.
- Message system: `fsck_send_msg()`, `fsck_ref_msg()`, `msg_defs`.
- Byte swapping: `ujfs_swap_*()` and `swap_multiple()` helpers.
