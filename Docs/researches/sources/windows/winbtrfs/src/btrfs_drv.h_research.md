# File Research: sources/windows/winbtrfs/src/btrfs_drv.h

## Role

`btrfs_drv.h` is the central private driver header for WinBtrfs. It establishes Windows kernel build compatibility, global constants, core in-memory filesystem objects, lock helpers, debug/logging shims, and cross-module function prototypes for most of the driver.

## Major Definitions

- Build and compatibility setup: forces `_WIN32_WINNT`/`NTDDI_VERSION`, includes `ntifs.h`, `ntddk.h`, Mount Manager and WDM headers, then pulls in on-disk Btrfs definitions from `btrfs.h` and the public ioctl ABI from `btrfsioctl.h`.
- Driver constants: pool tags, known extended attribute names and CRC hashes, maximum extent sizes, compression extent size, read-ahead granularity, Btrfs volume prefix, Linux/WSL reparse tags, and Windows feature constants missing from older headers.
- Core file model:
  - `fcb_nonpaged` owns file resources, paging resources, directory child locks, and section object pointers.
  - `fcb` is the in-memory inode/file-control block with FSRTL header, subvolume/inode identity, security descriptor, file locks/oplocks, cached extents, hardlinks, xattrs, alternate data stream state, directory-child hash/index lists, dirty flags, and metadata-change flags.
  - `file_ref` models a name/path reference to an FCB, including parent/child links, open counts, delete-on-close/POSIX-delete state, and dirty tracking.
  - `ccb` is the per-open context, carrying create options, directory query cursor, privileges, access mask, filename, case-sensitivity state, EA index, LXSS flag, and send-stream state.
- Tree and root model:
  - `tree`, `tree_data`, `tree_holder`, `traverse_ptr`, `root`, `root_nonpaged`, and batch/rollback structs define the in-memory B-tree cache and mutation staging model.
  - `batch_operation` covers deletes/inserts for inode refs, extrefs, dir items, xattrs, extent data, free-space entries, and generic tree items.
- Storage model:
  - `device`, `space`, `chunk`, `changed_extent`, `changed_extent_ref`, `partial_stripe`, `range_lock`, and `sys_chunk` represent devices, allocation ranges, chunks, delayed extent reference updates, RAID/stripe bookkeeping, and system chunks.
  - `write_data_stripe`, `write_data_context`, and `tree_write` describe multi-device write operations and delayed tree writes.
- Volume/control objects:
  - `device_extension` is the main VCB. It owns mount options, superblock, sector/checksum sizes, device/chunk/root/tree lists, all major locks, dirty FCB/fileref/subvolume lists, cache lookasides, flush thread state, calculation threads, balance/scrub/send state, and root/dummy FCBs.
  - `control_device_extension`, `bus_device_extension`, `volume_device_extension`, `pdo_device_extension`, and `volume_child` model non-filesystem control/bus/PnP devices and discovered Btrfs volumes.
- Background operations:
  - `calc_job`, `drv_calc_thread`, and `drv_calc_threads` define the checksum/compression worker queue used by `calcthread.c`.
  - `balance_info`, `scrub_info`, and `scrub_error` hold long-running balance and scrub state.
  - `send_info` tracks send-subvolume worker state.

## Inline Logic

- Lock helpers wrap shared/exclusive acquisition and release of `Vcb->fcb_lock`, with SAL annotations.
- `map_user_buffer` maps MDL-backed IRP buffers or falls back to `Irp->UserBuffer`.
- `unix_time_to_win` and `win_time_to_unix` convert Btrfs timestamps to Windows 100ns FILETIME epoch and back.
- `get_raid0_offset` maps a logical RAID0 offset to stripe offset and stripe index.
- `make_file_id` packs a subvolume id and inode into Windows' 64-bit file-id space.
- `keycmp`, `sector_align`, `is_subvol_readonly`, `get_extent_data_len`, and `get_extent_data_refcount` provide common Btrfs key, alignment, readonly, and extent-ref helpers.
- `fcb_oplock` abstracts old/new FSRTL advanced FCB header layouts; `fast_io_possible` combines oplock, lock, and readonly checks.
- `write_fcb_compressed` centralizes compression eligibility: excludes NODATACOW, metadata/cache/root inodes, page files, and NOCOMPRESS unless mount force-compression is set.
- `fcb_alloc_size` maps directory/sparse/regular allocation-size reporting.

## Cross-Module API Surface

This header declares the driver-wide interfaces for:

- Driver/device lifecycle and PnP: `AddDevice`, mount manager thread/callbacks, disk/volume arrival and removal, PDO/volume helpers, boot helpers.
- B-tree operations: item find/next/prev, load/free tree, insert/delete item, batch commit, rollback, tree-difference scanning.
- Create/open/name handling: open FCB/fileref, load directories, add directory children, lookup by inode/name, mode inheritance.
- Read/write/flush: file read/write paths, extent insertion, chunk allocation, physical I/O, checksums, tree checksums, partial stripe flushing, cache flushing.
- Free space and extent tree: free-space cache loading/updating, space-list add/subtract/merge, extent refcount changes, changed-extent tracking.
- User-visible IRP handlers: create, read, write, directory control, security, file information, EA, FSCTL, device control, PnP.
- Compression/checksum workers: zlib/lzo/zstd compress/decompress, compressed write path, checksum/compression job helpers, calculation thread routine.
- Balance, scrub, send, registry, reparse, security mapping, galois/RAID6 math, worker thread jobs, cache manager callbacks.

## Dependencies

- Depends on Windows kernel primitives: `ERESOURCE`, `FAST_MUTEX`, `KEVENT`, `KSPIN_LOCK`, `FILE_OBJECT`, `IRP`, `VPB`, `MDL`, FSRTL headers, oplocks, cache manager, Mount Manager, PnP notifications, and kernel process/thread APIs.
- Depends on local on-disk format definitions from `btrfs.h` and public WinBtrfs ioctl structs from `btrfsioctl.h`.
- Provides declarations consumed by almost every `.c` file in `src`.

## Research Notes

- This is a high-coupling driver umbrella header, not a narrow interface file. It intentionally centralizes the private ABI among subsystems.
- Locking is an important theme: SAL lock annotations document intended order, notably `tree_lock` before `fcb_lock`, and chunk locking is optionally instrumented under `DEBUG_CHUNK_LOCKS`.
- Several compatibility definitions fill gaps between MSVC, MinGW/GCC, older WDKs, and newer Windows FS features. This header is therefore both architectural glue and portability glue.
- The header includes private declarations for newer Windows runtime APIs and PEB structures, implying some routines dynamically probe OS behavior rather than depending only on static WDK availability.
