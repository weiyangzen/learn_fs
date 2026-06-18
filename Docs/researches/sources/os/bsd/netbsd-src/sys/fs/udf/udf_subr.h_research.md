# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.h

## Purpose

`udf_subr.h` is the internal UDF support header. It declares the shared helper API used across NetBSD’s UDF filesystem implementation and provides the `VFSTOUDF(mp)` mount-data conversion macro.

It is not limited to declarations implemented in `udf_subr.c`; it also exposes functions implemented across sibling UDF source files such as allocation, read/write, vnode operations, rename, and disc strategy modules.

## API Groups

### Mount and Device Helpers

Declared functions include:
- Disc and track inspection: `udf_update_discinfo()`, `udf_update_trackinfo()`.
- Track search and writable track setup: `udf_search_tracks()`, `udf_search_writing_tracks()`.
- MMC write setup and cache synchronization: `udf_setup_writeparams()`, `udf_mmc_synchronise_caches()`, `udf_synchronise_caches()`.

### Descriptor Helpers

The header exposes:
- Tag/FID sizing: `udf_fidsize()`, `udf_tagsize()`.
- Tag validation and CRC recomputation: `udf_check_tag()`, `udf_check_tag_payload()`, `udf_validate_tag_sum()`, `udf_validate_tag_and_crc_sums()`.
- Physical descriptor read/write: `udf_read_phys_sectors()`, `udf_write_phys_sectors()`, `udf_read_phys_dscr()`, `udf_write_phys_dscr_sync()`, `udf_write_phys_dscr_async()`.
- Logical-volume descriptor handling: `udf_create_logvol_dscr()`, `udf_free_logvol_dscr()`, `udf_read_logvol_dscr()`, `udf_write_logvol_dscr()`.

### Volume Discovery and Lifecycle

Declared mount-time helpers:
- `udf_read_anchors()`
- `udf_read_vds_space()`
- `udf_process_vds()`
- `udf_read_vds_tables()`
- `udf_read_rootdirs()`

Declared writable-volume helpers:
- `udf_open_logvol()`
- `udf_close_logvol()`
- `udf_writeout_vat()`
- `udf_write_physical_partition_spacetables()`
- `udf_write_metadata_partition_spacetable()`
- `udf_do_sync()`
- `udf_synchronise_metadatamirror_node()`

### Translation and Allocation

The header declares the mapping and allocation contract:
- Logical-to-physical translation: `udf_translate_vtop()`, `udf_translate_vtop_list()`, `udf_translate_file_extent()`.
- Allocation descriptor access: `udf_get_adslot()`, `udf_append_adslot()`.
- VAT access: `udf_vat_read()`, `udf_vat_write()`.
- Reservation/allocation/free: `udf_reserve_space()`, `udf_allocate_space()`, `udf_free_allocated_space()`, `udf_cleanup_reservation()`.
- Late allocation and resize: `udf_late_allocate_buf()`, `udf_grow_node()`, `udf_shrink_node()`, `udf_resize_node()`.
- Free-space calculation: `udf_calc_freespace()`.

### Node Lifecycle

Node-related declarations include:
- Unique ID advancement: `udf_advance_uniqueid()`.
- Lock wrappers: `UDF_LOCK_NODE()` and `UDF_UNLOCK_NODE()` record source file/line for lock debugging.
- Node locking functions: `udf_lock_node()`, `udf_unlock_node()`.
- Node lookup/write/dispose: `udf_get_node()`, `udf_writeout_node()`, `udf_dispose_node()`.
- Node tree and ICB helpers: `udf_init_nodes_tree()`, `udf_get_node_id()`, `udf_compare_icb()`.

### File Buffer I/O and Disc Strategy

The header declares:
- File buffer read/write entry points: `udf_read_filebuf()`, `udf_write_filebuf()`.
- Descriptor fixup helpers: `udf_fixup_fid_block()`, `udf_fixup_internal_extattr()`, `udf_fixup_node_internals()`.
- Disc strategy lifecycle and queueing: `udf_discstrat_init()`, `udf_discstrat_finish()`, `udf_discstrat_queuebuf()`.

### Descriptor Creation and Identity

Shared creators include:
- `udf_write_terminator()`
- `udf_inittag()`
- `udf_set_regid()`
- `udf_add_domain_regid()`
- `udf_add_udf_regid()`
- `udf_add_impl_regid()`
- `udf_add_app_regid()`

### Directory and Name Handling

Directory helpers:
- `udf_osta_charset()`
- `udf_read_fid_stream()`
- `udf_lookup_name_in_dir()`
- `udf_create_node()`
- `udf_delete_node()`
- `udf_chsize()`
- `udf_dir_detach()`
- `udf_dir_attach()`
- `udf_dir_update_rootentry()`
- `udf_dirhash_fill()`

Name conversion:
- `udf_to_unix_name()`
- `unix_to_udf_name()`

### Times, Modes, Ownership

The header exposes:
- Dirty list helpers: `udf_add_to_dirtylist()`, `udf_remove_from_dirtylist()`.
- Timestamp update: `udf_itimes()`, `udf_update()`.
- Access mode and ownership conversion: `udf_getaccessmode()`, `udf_setaccessmode()`, `udf_getownership()`, `udf_setownership()`.
- UDF timestamp conversion: `udf_timestamp_to_timespec()`, `udf_timespec_to_timestamp()`.

### Vnode Operations

The header declares UDF vnode operation entry points:
- Lifecycle: `udf_inactive()`, `udf_reclaim()`.
- Attribute/path/access: `udf_getattr()`, `udf_setattr()`, `udf_pathconf()`, `udf_access()`.
- Open/close/read/write: `udf_open()`, `udf_close()`, `udf_read()`, `udf_write()`.
- Lookup and creation/removal: `udf_lookup()`, `udf_create()`, `udf_mknod()`, `udf_link()`, `udf_symlink()`, `udf_rename()`, `udf_remove()`, `udf_mkdir()`, `udf_rmdir()`.
- Directory/symlink: `udf_readdir()`, `udf_readlink()`.
- Strategy/fsync/locking: `udf_trivial_bmap()`, `udf_vfsstrategy()`, `udf_fsync()`, `udf_advlock()`.

## Design Role

This header is the internal coupling point for the UDF implementation. It makes the filesystem’s mount, vnode, allocation, descriptor, directory, and media-strategy layers visible to one another. The API is broad and exposes many concrete on-disc UDF concepts directly, which matches the implementation style of this filesystem: explicit descriptor manipulation rather than a narrow abstraction boundary.
