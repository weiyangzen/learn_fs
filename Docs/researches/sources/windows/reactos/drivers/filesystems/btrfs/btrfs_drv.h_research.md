# File Research: sources/windows/reactos/drivers/filesystems/btrfs/btrfs_drv.h

## Purpose

Central private driver header for the ReactOS-imported WinBtrfs filesystem driver. It defines the driver-wide Windows/ReactOS compatibility layer, core in-memory Btrfs objects, synchronization conventions, helper inlines, debug/logging macros, and cross-module prototypes used by the Btrfs driver implementation.

## Main Contents

- Platform setup:
  - Handles `__REACTOS__`, `_MSC_VER`, GCC/Clang warning pragmas, Windows target macros, missing DDK declarations, SAL compatibility, `try/except/finally` compatibility, and ReactOS-specific includes.
  - Includes `btrfs.h` and `btrfsioctl.h`, making this the bridge between on-disk Btrfs structures, user IOCTL ABI, and driver-private state.
- Driver constants:
  - Node types, pool tags, UID/GID defaults, xattr names and CRC hashes, max extent sizes, compressed extent size, read-ahead granularity, reparse tags, device name prefix, FSCTL definitions not present in older headers, and POSIX mode macros.
- Core object model:
  - `fcb_nonpaged`, `fcb`, `file_ref`, `ccb`: file control block, per-open context, name/reference tracking, xattrs, ADS data, cached extents, security descriptor state, dirty flags, oplock and lock state.
  - `extent`, `hardlink`, `dir_child`, `xattr`: in-memory file metadata children and extent representation.
  - `tree`, `tree_data`, `tree_holder`, `traverse_ptr`, `root`: Btrfs tree/root cache structures and traversal state.
  - `device`, `chunk`, `space`, `range_lock`, `partial_stripe`, `changed_extent`, `changed_extent_ref`: physical devices, allocation chunks, free-space/range locking, RAID partial stripes, and delayed extent-ref accounting.
  - `device_extension`: main mounted filesystem VCB containing mount options, superblock, roots, chunks, global locks, FCB lists, dirty lists, flush thread state, checksum/compression worker threads, balance/scrub/send state, and lookaside lists.
  - `volume_device_extension`, `pdo_device_extension`, `volume_child`, `bus_device_extension`, `control_device_extension`: PnP/volume/bus/control device state for multi-device Btrfs volumes.
- Worker/job structures:
  - `calc_job`, `drv_calc_thread`, `drv_calc_threads` for checksum, hash, compression, and decompression work.
  - `balance_info`, `scrub_info`, `scrub_error`, `send_info` for long-running maintenance operations.
- Inline helpers:
  - FCB lock wrappers.
  - `map_user_buffer`.
  - Btrfs/Windows time conversion.
  - RAID0 offset calculation.
  - Btrfs key comparison.
  - Sector alignment.
  - Subvolume readonly checks.
  - Extent ref data sizing/refcount helpers.
  - File ID packing using subvolume and inode.
  - Oplock lookup and fast-IO feasibility.
  - Compression policy via `write_fcb_compressed`.
  - Allocation size calculation via `fcb_alloc_size`.
  - POSIX `makedev`, `major`, `minor` equivalents.
- Cross-module declarations:
  - Prototypes for create/open, read/write, flush, tree functions, cache manager callbacks, compression, checksum workers, free-space cache, extent tree, security, EA, reparse, PnP, volume management, registry, balance, scrub, send, RAID helpers, and boot helpers.

## Architecture Notes

This file is the coordination point for almost every Btrfs driver module. The important ownership boundaries are:

- `device_extension` is the mounted-volume aggregate and owns global structures such as roots, chunks, dirty lists, worker threads, and cache/thread state.
- `fcb` represents inode-backed file state; `file_ref` represents name/reference/open-parent relationships.
- `tree`/`root`/`traverse_ptr` model loaded Btrfs metadata trees and item traversal.
- `chunk`/`device`/`space` model logical-to-physical allocation and free-space accounting.
- `calc_job` connects checksum/hash/compression work in `calcthread.c` and codec routines in `compress.c`.

## Synchronization

The header documents and encodes several lock-order assumptions:

- `_Create_lock_level_` and `_Lock_level_order_(tree_lock, fcb_lock)` establish tree lock before FCB lock.
- `fcb_lock`, `tree_lock`, chunk locks, dirty-list locks, range locks, and partial-stripe locks are embedded in driver state.
- Some prototypes are annotated with `_Requires_lock_held_`, `_Requires_exclusive_lock_held_`, or `_Releases_lock_`, making lock requirements visible across modules.
- `acquire_chunk_lock`/`release_chunk_lock` optionally track held chunk locks under `DEBUG_CHUNK_LOCKS`.

## Dependencies

- Depends on Windows kernel APIs: NT I/O manager, cache manager, FsRtl, resources, spinlocks, events, MDLs, PnP, mount manager, VPB/device objects.
- Depends on Btrfs on-disk type definitions from `btrfs.h`.
- Imports public/private Btrfs control structures from `btrfsioctl.h`.
- Declares codec/checksum integration points used by `compress.c`, `calcthread.c`, `crc32c.c`, and `crc32c.S`.

## Research Notes

- Any change to structures in this header has wide blast radius because many C files include it and share these layouts.
- `btrfsioctl.h` structures are user-visible ABI, while most structures here are driver-private.
- Compression policy is centralized in `write_fcb_compressed`: it avoids compression for NODATACOW files, root/cache inodes, and paging files; it honors force-compress, inode flags, and mount options.
- File IDs are deliberately lossy because Windows exposes 64-bit file IDs while Btrfs uses separate 64-bit subvolume and inode identifiers.
