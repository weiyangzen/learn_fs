# File Research: sources/windows/reactos/drivers/filesystems/btrfs/btrfs.c

## Scope

This report covers the complete `btrfs.c` file in the ReactOS-imported WinBtrfs filesystem driver. The file is the central driver lifecycle and mount implementation: it registers dispatch routines, creates the control and bus devices, mounts Btrfs volumes, reads and validates superblocks, loads roots/chunks/devices, handles volume information IRPs, tracks dirty FCB/file-reference state, performs cleanup/close/delete-on-close behavior, and tears down mounted volumes.

## Primary Responsibilities

- Defines global driver state: control/bus device objects, mounted VCB list, UID/GID mappings, registry-derived mount defaults, debug logging state, PnP notification handles, and optional system routine pointers.
- Implements `DriverEntry()`, `DriverUnload()`, `AddDevice()`, shutdown, power, system-control, filesystem-control, cleanup, close, flush, lock-control, query-volume, and set-volume dispatch paths.
- Mounts a filesystem in `mount_vol()` by validating Btrfs identity, loading registry options, checking feature flags, creating a filesystem device object, loading superblock/chunk/root/device state, initializing FCBs/lookasides/cache state, creating flush and checksum worker threads, and publishing the VPB mount.
- Provides core helpers exported or used by other Btrfs driver modules: `get_xattr()`, `create_root()`, `delete_fileref()`, `get_file_attributes()`, `sync_read_phys()`, `check_superblock_checksum()`, `dev_ioctl()`, `find_device_from_uuid()`, `init_device()`, `protect_superblocks()`, `find_chunk_usage()`, `find_default_subvol()`, `init_file_cache()`, `check_file_name_valid()`, `chunk_lock_range()`, `chunk_unlock_range()`, and `log_device_error()`.
- Owns object lifetime for FCBs and file references through refcount decrement, reaping, recursive fileref cleanup, and full VCB uninitialization.

## Entry Points And Control Flow

`DriverEntry()` initializes OS-version-dependent routine pointers, logging, CPU feature selection, dispatch tables, fast I/O dispatch, the `\Btrfs` control device and symbolic link, cache subsystem, global lists/resources, registry watcher, a synthetic bus device, PnP notification callbacks, degraded-mount wait thread, and filesystem registration.

`AddDevice()` handles Btrfs PDOs discovered by PnP. It creates a named volume device under the Btrfs volume prefix, builds an ARC-name symbolic link, registers the volume interface, attaches to the physical stack, marks boot volumes, and stores the `volume_device_extension` in the PDO extension.

`drv_file_system_control()` dispatches mount, verify, and FSCTL requests. `IRP_MN_MOUNT_VOLUME` calls `mount_vol()`. User/kernel FS requests are forwarded to `fsctl_request()`. Verify calls `verify_volume()`, and failures on mounted volumes mark the VCB as removing.

`mount_vol()` is the dominant control path. It distinguishes Btrfs PnP volumes from raw/non-PnP devices, verifies superblock presence, opens or selects a read device, creates a filesystem device object, reads the newest valid superblock, applies mount options, enforces unsupported incompat/compat-ro feature policy, initializes lists/resources/lookasides, loads the chunk root and system chunks, discovers chunk items/devices, loads the root tree and all roots, clears stale free-space cache when required, creates volume/dummy/root FCBs and the root stream file, calculates per-device holes, publishes the VPB, starts the periodic flush thread and calculation threads, marks the volume mounted in the registry, and inserts the VCB into the global mount list.

`drv_cleanup()` performs per-handle cleanup: oplock checks, share removal, byte-range unlocks, directory notification cleanup, delete-on-close handling, POSIX delete finalization, cache flushing/purging, volume unlock release, reservation cleanup, fileref open-count decrement, and cache-map uninitialization.

`close_file()` handles IRP close by freeing CCB buffers, cancelling active send operations attached to the CCB, uninitializing cache maps, triggering VCB teardown when the last open file closes during removal, and releasing the fileref or FCB reference.

`uninit()` transitions a mounted VCB into teardown: clears VPB mount state, removes it from global lists, stops balance/scrub/send/calculation/flush threads, marks registry unmounted, reaps volume/dummy/root/all FCBs, frees system chunks, roots, chunks, devices, scrub errors, resources, lookaside lists, detaches from the storage stack, and deletes the filesystem device object.

`do_shutdown()` dismounts every mounted VCB, removes drive letters for volume devices, replaces VPBs for synthetic volume objects, unregisters filesystem and PnP notifications, detaches/deletes the bus object, and deletes the control device.

## Filesystem Metadata Loading

`read_superblock()` reads all possible Btrfs superblock mirrors that fit on the device, validates magic, sector/node-size sanity, and checksum, then keeps the valid superblock with the highest generation.

`check_superblock_checksum()` supports CRC32C, xxHash64, SHA-256, and BLAKE2 checksums over the superblock body. It is used for mount probing, verify, wakeup validation, and raw superblock checks.

`load_sys_chunks()` parses the bootstrap system chunk array embedded in the superblock into `sys_chunk` records.

`load_chunk_root()` scans the chunk tree for `DEV_ITEM` and `CHUNK_ITEM` records. It reconciles known devices from the PnP child list, optionally creates degraded missing-device placeholders, initializes `chunk` objects, validates stripe counts, maps chunk stripes to `device` pointers, sets profile flags, initializes per-chunk locks/lists, and establishes default data/metadata/system profiles when no chunk of a class exists.

`look_for_roots()` scans the root tree for `ROOT_ITEM` and `ROOT_BACKREF` records, calls `add_root()`, records parent subvolume relationships, and creates a missing data-relocation root on writable mounts.

`find_chunk_usage()` reads extent-tree `BLOCK_GROUP_ITEM` records to populate `chunk->used`, `chunk->oldused`, and `superblock.bytes_used`.

`find_disk_holes()` scans device extents for each device and builds a free physical-space list, subtracting the first MiB to match Linux allocation behavior.

`protect_superblocks()` removes physical/logical ranges that overlap Btrfs superblock mirrors from a chunk's allocatable space, with layout-specific handling for single/duplicate/RAID1/RAID10/RAID5/RAID6/RAID1C3/RAID1C4-style profiles.

## File, Directory, And Notification State

`mark_fcb_dirty()` and `mark_fileref_dirty()` insert objects into VCB dirty lists and set `Vcb->need_write`, coupling this file to `flushthread.c`.

`delete_fileref()` implements unlink/delete-on-close logic for normal files, alternate data streams, hardlinks, orphaned files, and subvolume references. It updates link counts, inode timestamps/sequences, parent directory size/timestamps, hardlink lists, directory-child hashes, deleted ADS children, root drop lists, cache-map state, and dirty flags. `delete_fileref_fcb()` excises extents and zeros cached file sizes when the underlying file object is actually deleted.

`send_notification_fileref()`, `send_notification_fcb()`, and `queue_notification_fcb()` translate dirty fileref/FCB activity into `FsRtlNotifyFilterReportChange()` calls, including hardlink path expansion through parent filerefs.

`get_file_attributes()` derives Windows file attributes from Btrfs type, DOS attribute xattr, dotfile/default-subvolume hiding, symlink reparse semantics, archive defaults, and readonly subvolume flags.

`check_file_name_valid()` enforces Windows/Btrfs component rules: non-empty, <=255 UTF-16 code units, no invalid Windows characters unless POSIX/stream semantics allow them, no NUL or slash, no `.`/`..`, no unpaired UTF-16 surrogates, and <=255 UTF-8 bytes for Linux interoperability.

## Device, PnP, Power, And Verification

`init_device()` records removability, change count, disk/partition numbers, readonly state, ATA flush-cache support, TRIM support, device stats, and per-device trim list state.

`find_device_from_uuid()` searches already loaded devices and the parent PDO child list, dynamically adding devices when found. It supports degraded operation when devices are missing and mount options allow it.

`verify_device()` and `verify_volume()` handle removable-media and wrong-volume validation by checking device verify state, re-reading the primary superblock, validating UUID/checksum, and degrading missing devices when permitted.

`drv_power()` flushes dirty mounted volumes before sleep/hibernate while disks are still awake, and queues a wakeup validation work item to detect whether another OS modified the filesystem generation while suspended.

`check_after_wakeup()` reads every device's superblock after resume and forces a remount/teardown if the on-disk generation is newer than expected.

## Low-Level Helpers

`sync_read_phys()` manually builds synchronous raw read IRPs for buffered, direct, and neither-I/O device stacks, with optional verify override. It is central to superblock probing and validation.

`dev_ioctl()` builds synchronous device-control IRPs and optionally overrides verify volume.

`utf8_to_utf16()` and `utf16_to_utf8()` provide Vista-and-earlier-compatible conversions with replacement-character handling and buffer-length reporting.

`do_xor_basic()` is the fallback XOR routine, with ARM NEON and 64-bit word loops where available. `check_cpu()` selects hardware CRC32C and SSE2/AVX2 XOR implementations on non-ReactOS x86/x64 builds.

`chunk_lock_range()` and `chunk_unlock_range()` implement per-chunk byte-range exclusion using a list of `range_lock` records, the owning thread pointer, and an event for waiters.

## Dependencies

This file depends on Windows kernel/IFS APIs for driver/device creation, VPB manipulation, IRPs, PnP notifications, power forwarding, file locks, oplocks, cache manager integration, resources, lookaside lists, events, timers, work items, process/PEB inspection, registry access, and storage IOCTLs.

It depends heavily on other Btrfs driver modules for create/read/write/dirctrl/fileinfo/security/fsctl/device-control/pnp dispatches, tree search and mutation, cache callbacks, FCB creation, directory loading, free-space cache clearing, rollback, extent excision, volume locking/dismount, registry options, PnP volume-child management, balance/scrub/send operations, checksum implementations, and mount-manager helpers.

## Important Invariants And Risks

- Mount correctness depends on loading the chunk root before arbitrary logical tree access, because logical-to-physical mapping requires chunk/device state.
- `mount_vol()` increments `superblock.generation` early on writable mounts; many later writes and generation comparisons assume that convention.
- Unsupported incompat flags reject the mount; unsupported compat-ro flags force readonly. Expanding supported features without matching implementation would risk metadata corruption.
- Several teardown paths are partial on mount failure. The error cleanup deletes many initialized objects but does not mirror full `uninit()` coverage for every possible partially initialized field.
- FCB/fileref lifetime is refcount-driven and resource-protected in many but not all places. The file contains FIXME notes for fileref locking, recursive fileref reaping in kernel mode, and root/volume freeing.
- Delete-on-close and POSIX delete paths mutate directory trees, hardlink lists, extents, cache maps, orphan behavior, and dirty queues under multiple locks; lock ordering is explicitly important around `fileref_lock` and `Header.Resource`.
- `load_chunk_root()` degraded-device behavior can create device records with no `devobj`; every IO path must continue to check for missing devices.
- `protect_superblocks()` has profile-specific arithmetic for logical-to-physical coverage. Errors there could allocate over superblock mirror areas.
- Power resume validation assumes generation monotonicity is enough to detect unsafe external modification.
- The ReactOS build disables some Windows-specific behavior such as filesystem-type lying and CPU dispatch sections; portability depends on the `__REACTOS__` conditionals remaining accurate.
