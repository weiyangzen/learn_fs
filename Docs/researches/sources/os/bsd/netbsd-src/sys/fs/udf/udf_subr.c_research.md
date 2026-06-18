# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.c

## Purpose

`udf_subr.c` is the large support implementation for NetBSD’s in-kernel UDF filesystem. It handles most mount-time UDF format interpretation and much of the common vnode support machinery used by `udf_vfsops.c` and vnode operations.

Major responsibilities include:
- Device/media and MMC track discovery.
- Descriptor tag validation, CRC maintenance, and descriptor sizing.
- Anchor, VDS, logical volume integrity, VAT, sparable partition, metadata partition, and root directory discovery.
- Logical volume open/close sequencing for writable media.
- Node loading, descriptor lifecycle, dirty/writeout handling, and genfs integration.
- Directory FID parsing, dirhash population, lookup, attach, detach, and parent update.
- UDF/Unix name, permission, ownership, and timestamp conversion.
- File-buffer read/write translation handoff to lower UDF mapping and disc strategy code.

## Key Flows

### Media and Track Discovery

The file starts with debug dump helpers for `mmc_discinfo` and `mmc_trackinfo`, then implements:
- `udf_update_discinfo()`: asks the device for MMC disc info, or synthesizes disc-like information for ordinary disk partitions via `getdisksize()`.
- `udf_update_trackinfo()`: reads MMC track info, or synthesizes a single closed track for partition-backed mounts.
- `udf_setup_writeparams()`: prepares MMC write parameters for recordable media.
- `udf_mmc_synchronise_caches()`: issues MMC cache synchronization for writable non-partition media.
- `udf_search_tracks()`: maps requested session number to first/last track.
- `udf_search_writing_tracks()`: identifies writable data and metadata tracks, attempts damaged-track repair, and rejects media without writable data/metadata tracks.

This is the media abstraction layer that lets UDF mount on both optical MMC devices and regular block devices.

### Descriptor Validation

Descriptor helpers include:
- `udf_check_tag()`: validates 16-byte UDF descriptor tag checksum.
- `udf_check_tag_payload()`: validates descriptor payload CRC.
- `udf_validate_tag_sum()` and `udf_validate_tag_and_crc_sums()`: recompute tag checksum and payload CRC before writing.
- `udf_tagsize()`: computes descriptor size for known descriptor types, usually rounded to logical block size.
- `udf_fidsize()`: computes exact FID length without sector rounding.

These routines are central to safely reading and rewriting on-disc UDF structures.

### Anchor and Volume Descriptor Processing

Mount-time discovery proceeds through:
- `udf_read_anchor()` and `udf_read_anchors()`: locate AVDPs around track start/end positions.
- `udf_read_vds_extent()` and `udf_read_vds_space()`: read the main/reserve Volume Descriptor Sequence.
- `udf_process_vds_descriptor()`: records primary volume, logical volume, partition, implementation, and unallocated-space descriptors.
- `udf_process_vds()`: validates descriptor completeness, checks OSTA UDF compliance, retrieves logical volume integrity, decodes partition maps, determines virtual-to-physical mapping types, selects allocation strategies, and selects the disc strategy implementation.

Important partition-map handling:
- Physical mappings become space-map allocations.
- Virtual mappings enable VAT and sequential allocation.
- Sparable mappings load sparing tables and use remap-on-error behavior.
- Metadata mappings identify metadata files and metadata bitmap behavior.

The code also contains compatibility handling for malformed/random physical partition numbers through `udf_find_raw_phys()`.

### Logical Volume Integrity

Logical volume integrity support is implemented through:
- `udf_retrieve_lvint()`: reads the logical volume integrity sequence, including chained extents, and records trace positions.
- `udf_loose_lvint_history()`: rewrites/reduces old integrity history when space runs out.
- `udf_writeout_lvint()`: updates timestamp and implementation ID, writes the current integrity descriptor, and appends a terminator if possible.

This is used by both mount/open and unmount/close paths to mark a writable volume open or closed.

### Space Tables and Metadata Partition Bitmap

Space table support includes:
- `udf_read_physical_partition_spacetables()`: reads unallocated and freed space bitmaps; explicitly rejects table-based unallocated/freed space descriptors as unsupported.
- `udf_write_physical_partition_spacetables()`: writes physical partition bitmaps synchronously.
- `udf_read_metadata_partition_spacetable()`: reads metadata bitmap file through the vnode layer.
- `udf_write_metadata_partition_spacetable()`: resizes and writes metadata bitmap contents.

Notes:
- Bitmap page backing is marked TODO.
- Physical unallocated/freed “space tables” are not supported and force read-write mount failure.
- Metadata write support is constrained; `udf_read_metadata_nodes()` explicitly notes metadata writing is disabled/not working in some paths.

### VAT and Sequential Media

VAT handling is substantial:
- `udf_vat_read()` and `udf_vat_write()` access and grow the in-memory VAT table.
- `udf_check_for_vat()` validates old UDF 1.50 VAT tails or UDF VAT file headers, loads the full VAT file, and updates logical volume info.
- `udf_search_vat()` scans likely VAT locations near the end of the session and retains the last accepted VAT node.
- `udf_update_vat_descriptor()` updates old/new VAT metadata before writeout.
- `udf_writeout_vat()` writes the VAT table file and fsyncs the VAT node.
- VAT LVExtension extended attributes are synchronized by `udf_update_lvid_from_vat_extattr()` and `udf_update_vat_extattr_from_lvid()`.

For sequential media close, `udf_close_logvol()` writes repeated VAT descriptors for Windows compatibility and optionally closes tracks/sessions/finalizes media.

### Sparable and Metadata Partition Support

Partition-specific mount helpers:
- `udf_read_sparables()`: loads one valid sparing table from the partition map.
- `udf_read_metadata_nodes()`: loads metadata main, mirror, and bitmap files as system vnodes.
- `udf_read_vds_tables()`: dispatches to VAT, sparing table, metadata node, and bitmap readers after partition maps are known.

System files are marked using `UDF_SET_SYSTEMFILE`, which sets `VV_SYSTEM`, takes an extra ref, and releases the lock.

### Root Directory Discovery

`udf_read_rootdirs()`:
- Translates and reads the File Set Descriptor sequence.
- Keeps the last valid FSD encountered.
- Updates stored logical volume names.
- Loads the root directory node.
- Optionally attempts to load the system stream directory, but currently ignores it.

### Logical Volume Open/Close

Writable mount open:
- `udf_open_logvol()` checks integrity state, write parameters, writable tracks, optional session-start validation, optional VAT writeout, marks integrity open, and writes LVID if required.

Unmount close:
- `udf_close_logvol()` writes VATs, closes session/tracks if requested, writes partition bitmaps, writes metadata partition descriptors/mirror, marks integrity closed, writes LVID, and synchronizes caches.

`udf_validate_session_start()` handles writing or copying the ISO/UDF VRS and initial anchor when opening a new sequential session.

### Genfs Integration and Buffer I/O

The file defines UDF genfs hooks:
- `udf_gop_alloc()`: reserves logical blocks before writes.
- `udf_gop_markupdate()`: maps genfs update flags to UDF inode flags.
- `udf_genfsops`: uses `genfs_gop_write_rwmap`.

Buffer helpers:
- `udf_read_filebuf()`: translates file logical blocks, handles internal/zero/unmapped cases, creates nested I/O buffers for mapped runs, and queues them to the selected disc strategy.
- `udf_write_filebuf()`: translates/late-allocates write runs through nested buffers and increments outstanding buffer accounting.
- `udf_read_internal()` and `udf_write_internal()` handle files stored inside FE/EFE descriptors.

Translation and allocation helpers such as `udf_translate_file_extent()`, `udf_reserve_space()`, `udf_allocate_space()`, `udf_grow_node()`, and `udf_shrink_node()` are called here but implemented elsewhere.

### Node Lifecycle

Node helpers include:
- `udf_get_node_id()` and `udf_compare_icb()` for identity/rbtree ordering.
- `udf_init_nodes_tree()` initializes the sync rbtree.
- `udf_loadvnode()` loads a vnode from an ICB address, follows indirect entries, accepts FE/EFE descriptors, loads allocation extension descriptors, sets vnode type, and initializes genfs state.
- `udf_get_node()` uses `vcache_get()` and locks the vnode.
- `udf_writeout_node()` writes dirty node descriptors and allocation extension descriptors.
- `udf_dispose_node()` tears down genfs state, dirhash, locks, allocation extension descriptors, FE/EFE memory, and returns the node to `udf_node_pool`.
- `udf_newvnode()` allocates one logical block for a new FE/EFE and initializes vnode/node state.
- `udf_create_node()` creates and attaches a new node into a directory, rolling back allocated descriptor space on failure.
- `udf_delete_node()` shrinks a file to zero, marks it clean/deleted, adjusts file counts, and frees descriptor space.
- `udf_resize_node()` dispatches grow/shrink.

Special file creation for block devices, char devices, FIFOs, and sockets returns `ENOTSUP`; comments note missing specfs/fifofs integration.

### Directory Operations

Directory support includes:
- `udf_read_fid_stream()`: reads one FID descriptor from a directory stream, validates tag and payload CRC, converts the UDF name to a `dirent`, synthesizes `".."` for parent FIDs, and advances the offset.
- `udf_dirhash_fill()`: builds a NetBSD `dirhash`, recording deleted FIDs as reusable free entries.
- `udf_lookup_name_in_dir()`: canonicalizes a Unix name through UDF name conversion, searches dirhash hits, rereads matching FIDs, and returns the target ICB.
- `udf_dir_attach()`: chooses a deleted FID slot or appends a new one, handles tag-split padding, writes the FID, updates link counts, and updates dirhash.
- `udf_dir_detach()`: marks a directory FID deleted, writes it back, optionally adjusts link counts, and removes dirhash entry.
- `udf_dir_update_rootentry()`: updates a directory’s `".."` FID after parent changes.

One conditional branch under `#ifndef UDF_COMPLETE_DELETE` appears to call `udf_read_fid_stream(vp, ...)` where the local directory vnode variable is `dvp`; this path depends on compile-time configuration and should be checked if `UDF_COMPLETE_DELETE` is ever disabled.

### Attributes, Names, Permissions, and Time

Conversion helpers:
- `udf_osta_charset()`, `udf_to_unix_name()`, and `unix_to_udf_name()` convert OSTA Compressed Unicode and UTF-8 names.
- `udf_perm_to_unix_mode()`, `unix_mode_to_udf_perm()`, and `udf_icb_to_unix_filetype()` translate UDF permissions/types.
- `udf_getaccessmode()` and `udf_setaccessmode()` read/write mode bits.
- `udf_getownership()` and `udf_setownership()` translate anonymous/nobody UID/GID conventions.
- `udf_timestamp_to_timespec()` and `udf_timespec_to_timestamp()` convert UDF timestamps.
- `udf_itimes()` applies access/change/update/modify/birth times.
- `udf_update()` updates timestamps, implementation ID, descriptor CRCs, and optionally fsyncs dirty nodes.

Extended attribute support:
- Searches internal FE/EFE EA space.
- Checks/calculates UDF implementation EA checksums.
- Can insert internal EAs while creating descriptors.
- Uses file-times EAs for FE creation time support.

### Synchronization

`udf_do_sync()`:
- Skips lazy sync.
- Iterates mount vnodes, selects dirty non-system UDF vnodes, inserts them into an rbtree, and runs three sync passes.
- Pass 1 fsyncs data only.
- Pass 2 fsyncs completed nodes.
- Pass 3 counts pending device/node I/O and waits for `MNT_WAIT`.
- Cleans the rbtree and releases vnode references.

This complements `udf_vfsops.c`’s `udf_sync()` wrapper.

## Dependencies

Includes and depends on:
- NetBSD kernel VFS, vnode, genfs, buf, dirhash, mount, kauth, device, disklabel, and clock APIs.
- UDF structure definitions from `ecma167-udf.h`, `udf_mount.h`, `udf.h`, and `udf_bswap.h`.
- Unicode helpers from `<fs/unicode.h>`.
- Disc strategy modules through `udf_discstrat_*()` and strategy globals.
- Allocation/readwrite helpers declared in `udf_subr.h` but implemented in other UDF files.

## Notable Constraints and Risks

- Sector sizes `>= 8192` are rejected by mount logic in `udf_vfsops.c`; this file assumes logical block and descriptor sizes fit current limits.
- Many descriptor and allocation paths rely on `KASSERT()`/`assert()` for invariants.
- Physical unallocated/freed space tables are unsupported; only bitmaps are handled.
- Metadata partition writing has comments indicating incomplete or disabled support.
- NFS file handles and `vget` support are not implemented in `udf_vfsops.c`, limiting export-style use.
- Directory corruption recovery is TODO; `udf_read_fid_stream()` reports broken entries but does not resynchronize.
- Internal allocation read/write paths note missing bounds checks for malicious `l_ea`/`inf_len` values.
- VAT and sequential media close handling is highly media-specific and intentionally compatibility-driven.
