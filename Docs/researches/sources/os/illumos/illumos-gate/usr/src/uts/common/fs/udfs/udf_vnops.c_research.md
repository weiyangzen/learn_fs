# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_vnops.c

## Purpose

`udf_vnops.c` implements the illumos UDFS vnode operation vector and the local read/write/page-cache helpers behind it. It is the bridge between generic VFS/VM operations and UDF inode, directory, allocation, symlink, and device I/O routines.

## Main Interfaces

The file installs `udf_vnodeops_template`, covering open/close/read/write, getattr/setattr/access, lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink, fsync/inactive/fid, rwlock/rwunlock/seek/frlock/space, getpage/putpage/map/addmap/delmap/pathconf/pageio, and vnode event support.

Internal helpers include `ud_rdwri`, `ud_rdip`, `ud_wrip`, `ud_getpage_miss`, `ud_getpage_ra`, `ud_page_fill`, `ud_putpages`, `ud_putapage`, `ud_iodone`, `ud_multi_strat`, and `ud_slave_done`.

## Behavior And Data Flow

Simple vnode calls mostly delegate into UDF inode/directory helpers: `ud_dirlook`, `ud_direnter`, `ud_dirremove`, `ud_iaccess`, `ud_itrunc`, `ud_iupdat`, `ud_syncip`, `ud_sync_indir`, and `ud_iinactive`.

Read and write paths use `segmap_getmapflt()` and `segmap_release()` for cached file I/O. `ud_wrip()` allocates blocks with `ud_bmap_write()` before increasing `i_size`, handles page creation and zero-fill for partial EOF pages, enforces process file-size limits, and clears set-id bits when required. `ud_rdip()` handles EOF/offset validation, read-ahead/free-behind hints, and synchronous read flush semantics.

The VM path handles UDF-specific storage shapes: embedded one-AD files, holes, logical blocks smaller than pages, and discontiguous extents. Multi-part I/O uses a master `mio_master_t` plus cloned slave buffers, with `ud_slave_done()` aggregating errors and completing the original buffer.

## Namespace And Metadata Semantics

Lookup uses DNLC first, then `ud_dirlook()`, and wraps device vnodes with `specvp()`. Create, mkdir, link, rename, remove, and rmdir serialize directory mutation with inode `i_rwlock` and rely on UDF directory helpers for on-disk updates. Rename has a filesystem-wide `udf_rename_lck`, validates sticky-directory removal access, rejects mounted-over directories, emits vnode pre/post rename events, links target first, then removes source.

Symlink creation converts POSIX path text into UDF `path_comp` records; readlink reverses those records into a slash-separated path. Readdir synthesizes `.` and converts UDF FIDs into `dirent64` records, skipping deleted entries and decompressing UDF names.

## Locking And State

`i_rwlock` serializes high-level read/write and directory mutation. `i_contents` protects inode size, metadata, and bmap/page operations. `i_tlock` protects transient flags, map counts, delayed write clustering, timestamps, and write throttle counters. Mandatory locking blocks mmap/frlock combinations when required.

## Notable Invariants And Risks

- `VNOMAP` vnodes reject mapping and page I/O paths.
- Writable mmap faults over holes may upgrade `i_contents` to writer and allocate blocks.
- UDF reports `_PC_FILESIZEBITS` as 41 because other block-number limits constrain practical file size.
- Delayed async putpage clustering uses `i_delayoff/i_delaylen` and is flushed on close or explicit putpage.
- Audit hotspots are symlink path-component buffer sizing, multi-I/O error cleanup, embedded-file page copying/tag CRC updates, partial write rollback after extending `i_size`, and write-throttle accounting in `ud_iodone()`.
