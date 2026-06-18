# File Research: sources/windows/winbtrfs/src/btrfs.c

## Role

`btrfs.c` is the central WinBtrfs filesystem-driver entry and mount orchestration unit. It wires the Windows driver object to dispatch routines implemented across the driver, owns global driver state, mounts and verifies Btrfs volumes, loads superblock/root/chunk/device metadata, manages file-reference/FCB lifetimes, handles shutdown/power/unload, and supplies shared helpers for names, attributes, notifications, physical I/O, checksums, and range locking.

## Main Responsibilities

- Defines supported Btrfs feature masks: `INCOMPAT_SUPPORTED` allows mixed backrefs, default subvols, mixed groups, LZO/ZSTD, big metadata, RAID56, extended irefs, skinny metadata, no-holes, metadata UUID, and RAID1C3/C4; `COMPAT_RO_SUPPORTED` allows free-space cache/tree validity, verity, and block-group tree.
- Declares global driver state: control and bus device objects, `VcbList`, UID/GID mapping lists, mount option defaults, registry/logging state, PnP notification handles, PDO list/mapping locks, degraded-mount timing state, boot lock, and dynamically resolved kernel routine pointers.
- Provides debug logging paths in `_DEBUG`: `DbgPrint`, serial-device writes, or log-file appends, protected by `log_lock`.
- Provides CPU feature selection for CRC32C and RAID XOR: SSE4.2 CRC32C, SSE2/AVX2 XOR on x86/x64, and ARM64 CRC32C where available; fallback XOR is `do_xor_basic`.
- Implements Windows IRP dispatchers present in this file: close, cleanup, flush buffers, query/set volume information, filesystem control, lock control, shutdown, power, and system control. Other major functions are assigned in `DriverEntry` but implemented in companion files.
- Implements mount/verify lifecycle: `mount_vol`, `verify_volume`, `verify_device`, `uninit`, `do_shutdown`, `DriverUnload`, `AddDevice`, and `DriverEntry`.

## Driver Entry And Global Setup

- `DriverEntry` reads OS version, initializes global locks/lists, copies `RegistryPath`, reads registry settings, optionally initializes debug logging, selects CPU-specific helpers, dynamically resolves optional Windows APIs, assigns all `DriverObject->MajorFunction` entries, initializes fast I/O dispatch, creates the `\Btrfs` control device and `\DosDevices\Btrfs` link, initializes caches, registry watching, and a private bus device.
- It reports/registers a Btrfs bus interface, invalidates bus relations, starts a three-second `degraded_wait_thread`, initializes `boot_lock`, registers PnP notifications for volume, hidden volume, and disk interfaces, starts the mount-manager thread, registers the filesystem with I/O manager, and calls `check_system_root`.
- `AddDevice` handles PDOs discovered by PnP code in other files. It finds the matching `pdo_device_extension`, creates a named volume device using `BTRFS_VOLUME_PREFIX` plus the filesystem UUID, creates an `\ArcName\btrfs(<uuid>)` symlink, registers a volume interface, attaches to the physical device stack, records the `volume_device_extension`, propagates removable/boot flags, enables the device interface, and returns success if already initialized.

## Mount Path

- `mount_vol` accepts only the master control device, rejects attempts to mount the driver's own PDO, and distinguishes normal Windows volume devices from private WinBtrfs volume devices by querying mountdev names and Btrfs PnP state.
- For PnP-backed multi-device filesystems, it validates child devices still contain Btrfs superblocks before mounting, chooses the first child for metadata reads, and refuses incomplete device sets unless degraded mounting is allowed and probing/wait conditions permit it.
- It creates the filesystem `DEVICE_OBJECT`, initializes the `device_extension`, resources, lists, lookaside lists, notification sync, and VCB pointers, reads the newest valid superblock copy, loads per-volume registry options, applies boot-subvolume override, rejects ignored volumes and unsupported incompat flags, converts unknown compatible-read-only flags into read-only mounts, increments the in-memory generation, clears an unreplayed log tree pointer, and sets checksum size based on superblock checksum type.
- It seeds the primary `device` from the superblock `DEV_ITEM`, detects readonly/removable/TRIM/flush support, adds the chunk root and system chunks, loads the chunk tree, validates device count/readonly state, loads the root tree and all root items, optionally finds chunk usage, clears invalid/outdated free-space cache state, and commits the mount-time batch list.
- It creates the volume FCB, dummy directory FCB, root FCB, root file reference, root stream file object, Cc cache map, loads root directory children, reads the root inode item, loads root security descriptor, computes root attributes, computes per-device free space holes, sets VPB mounted state, starts the flush thread and calculation worker threads, marks the registry volume mounted, looks for any persisted balance item, inserts the VCB into `VcbList`, and notifies `FSRTL_VOLUME_MOUNT`.
- Error cleanup is partial but broad: it deletes lookaside lists, dereferences root file or frees root references/FCBs, reaps volume FCB, deletes resources, frees device list entries, and deletes the newly created device object.

## Superblocks, Roots, Chunks, And Devices

- `sync_read_phys` builds and submits synchronous noncached read IRPs, handling buffered, direct, and neither I/O stacks and optional `SL_OVERRIDE_VERIFY_VOLUME`.
- `check_superblock_checksum` supports CRC32C, XXHASH, SHA256, and BLAKE2 superblock checksum types.
- `read_superblock` reads each address in `superblock_addrs`, verifies magic, sanity-checks sector/node sizes, validates checksum, and chooses the valid copy with the highest generation.
- `load_sys_chunks` parses the superblock system-chunk array into `sys_chunk` entries used to bootstrap logical-to-physical mapping.
- `add_root`, `look_for_roots`, and `create_root` allocate root structures, attach tree holders, initialize per-root locks and FCB hash pointers, copy `ROOT_ITEM` payloads, track known special roots in VCB fields, compute last inode for writable roots, and create the data relocation root if missing on writable filesystems.
- `load_chunk_root` scans chunk-root items, merges `DEV_ITEM` data with known devices/PNP children, constructs placeholder missing devices for degraded mounts, allocates `chunk` structures and stripe-device arrays for `TYPE_CHUNK_ITEM`, validates RAID10 stripe shape and nonzero stripe count, tracks data/metadata/system allocation profiles, and initializes per-chunk locks/lists/range-lock state.
- `find_device_from_uuid` first searches mounted devices, then PnP children, lazily creating a `device` when a matching child exists.
- `init_device` records removable state/change count, storage device numbers, readonly state, ATA flush-cache support, TRIM support, and initializes stats/trim lists.
- `find_disk_holes` reads device stats and `DEV_EXTENT` items to build each device free-space list, then removes the first MiB to match Linux allocation expectations.
- `protect_superblocks` removes logical allocation ranges that would cover physical Btrfs superblock locations for single/dup/RAID1/RAID1C3/RAID1C4, RAID0, RAID10, RAID5, and RAID6 layouts.
- `find_chunk_usage` reads `BLOCK_GROUP_ITEM` records from the extent root or block-group tree and updates chunk usage plus `superblock.bytes_used`.
- `find_default_subvol` honors explicit `subvol_id`, otherwise follows the `default` directory item when the default-subvolume incompat flag is set, and falls back to `BTRFS_ROOT_FSTREE`.

## File/Directory State And Deletion

- `mark_fcb_dirty` and `mark_fileref_dirty` set dirty bits, increment references, add entries to VCB dirty lists, and mark the volume as needing writeback.
- `free_fcb`, `reap_fcb`, and `reap_fcbs` implement FCB reference decrement and full reclamation: list unlinking, dropped-root cleanup, resource deletion, lookaside return/free, security/xattr/ADS/reparse buffers, extents, hardlinks, xattrs, dir children, hash arrays, file locks, and oplocks.
- `free_fileref`, `reap_fileref`, and `reap_filerefs` maintain file-reference counts and recursively reclaim file-reference subtrees when references reach zero.
- `close_file` frees CCB query/name buffers, cancels active send contexts, uninitializes cache maps, decrements open-file count, triggers `uninit` during removal when last open closes, and frees the fileref or FCB reference.
- `drv_cleanup` is the high-risk close-time path: removes share access and locks, notifies directory watches, handles delete-on-close and POSIX delete, unlocks volumes locked by the same file object, cancels reservations, decrements fileref open count, deletes or orphan-marks files when appropriate, flushes/purges cache when the last handle closes, uninitializes cache maps outside `tree_lock`, and marks `FO_CLEANUP_COMPLETE`.
- `delete_fileref` updates inode/link counts, handles ADS deletion, subvolume-reference/drop-root transitions, removes the child from parent directory hash/index lists, preserves old UTF-8 name/index for later metadata deletion, updates parent ctime/mtime/size, sends notifications, and marks affected FCBs/filerefs dirty.
- `delete_fileref_fcb` excises file extents, zeroes allocation/file/valid lengths, updates Cc file sizes when a file object is present, marks the FCB deleted, and marks ADS children deleted.

## Volume Information, Names, Attributes, And Xattrs

- `drv_query_volume_information` implements `FileFsAttributeInformation`, `FileFsDeviceInformation`, `FileFsFullSizeInformation`, `FileFsObjectIdInformation`, `FileFsSizeInformation`, `FileFsVolumeInformation`, and MSVC-only sector-size information. It reports Btrfs capabilities including case preservation, Unicode, streams, hard links, ACLs, reparse points, sparse files, object IDs, open-by-ID, EAs, block refcounting, and POSIX unlink/rename. It may report the filesystem name as `NTFS` for specific callers.
- `lie_about_fs_type` inspects the current process/module list and stack to return `NTFS` to selected Windows components/tools (`MPR.DLL`, `CMD.EXE`, `FSUTIL.EXE`, `STORSVC.DLL`, `IFSTEST.EXE`) and WOW64 callers for compatibility.
- `drv_set_volume_information` allows label updates on writable, unlocked volumes through `set_label`, rejecting invalid labels containing slash/backslash and enforcing `MAX_LABEL_SIZE` after UTF-8 conversion.
- `utf8_to_utf16` and `utf16_to_utf8` are Vista-and-below compatibility conversions that replace malformed sequences with U+FFFD and report `STATUS_SOME_NOT_MAPPED`; they also support sizing-only calls and buffer-overflow reporting.
- `extract_xattr` and `get_xattr` locate named extended attributes inside Btrfs `DIR_ITEM` payloads by CRC/key and copy values into pool memory.
- `get_file_attributes_from_xattr` parses `user.DOSATTRIB`-style hex attributes, and `get_file_attributes` combines xattr attributes with Btrfs type, dotfile hidden behavior, root/subvolume readonly state, archive/default flags, directory and symlink mapping.
- `check_file_name_valid` enforces Windows/Btrfs filename rules: nonempty, <=255 UTF-16 code units, no `/` or NUL, additional non-POSIX invalid characters, no unpaired surrogates, no `.` or `..`, and UTF-8 encoded length <=255 bytes or <=250 bytes for streams.

## Notifications, Locks, Cache, And Dispatch

- `send_notification_fileref`, `send_notification_fcb`, `queue_notification_fcb`, and `notification_work_item` convert filerefs/hardlinks into `FsRtlNotifyFilterReportChange` notifications, optionally queueing work items to avoid unsafe synchronous contexts.
- `drv_flush_buffers` checks oplocks, updates fast-I/O possibility, flushes the file cache for non-directories, and synchronizes through the paging resource.
- `drv_file_system_control` handles mount, user/kernel FSCTL forwarding to `fsctl_request`, and volume verification. Verification failures mark a mounted VCB as removing.
- `verify_device` and `verify_volume` recheck removable media/change counts, superblock magic/checksum/UUID, clear verify flags, degrade missing devices when allowed, and uninitialize when removal reaches zero opens.
- `drv_lock_control` delegates byte-range lock handling to `FsRtlProcessFileLock` after oplock checks.
- `chunk_lock_range` and `chunk_unlock_range` implement per-chunk overlapping range exclusion using a range-lock lookaside list, thread ownership, a resource, and an event.
- `init_file_cache` centralizes `CcInitializeCacheMap`, optional disk accounting, and read-ahead granularity.
- `calculate_total_space` converts Btrfs `total_bytes`/`bytes_used` into Windows allocation units adjusted for data RAID profile.

## Shutdown, Power, Unload, And Verification

- `uninit` marks the VCB removing, detaches VPB, removes from `VcbList`, stops balance/scrub/send/calculation/flush activity, marks registry unmounted, reaps FCBs/filerefs/roots/chunks/devices/sys_chunks/scrub errors, deletes resources and lookaside lists, closes flush thread handle, detaches and deletes the filesystem device.
- `do_shutdown` marks global shutdown, signals mount-manager thread, dismounts every mounted VCB, removes drive letters for private volume devices, creates replacement direct-write VPBs, frees volume devices when open count reaches zero, unregisters filesystem/PnP notifications, detaches/deletes the bus object, and deletes the control object.
- `drv_power` flushes dirty writable mounted filesystems before system sleep while disks are awake, frees cached trees after flush, queues `check_after_wakeup` on resume to detect external filesystem changes by generation, and forwards power IRPs down volume/filesystem/bus stacks.
- `check_after_wakeup` forces remount/removal if any device superblock generation exceeds the expected generation after resume.
- `drv_system_control` forwards WMI/system-control IRPs down attached stacks for volume, filesystem, and bus devices.
- `DriverUnload` removes the DOS link/control device, frees UID/GID mapping entries, closes debug resources, frees registry/log path buffers, and deletes global resources; it notes a FIXME for freeing volumes/devpaths.

## Dependencies And Cross-File Links

- Pulls public on-disk constants/structures from `btrfs.h`.
- Pulls internal driver types and prototypes from `btrfs_drv.h`.
- Calls tree and metadata helpers such as `find_item`, `find_next_item`, `insert_tree_item`, `delete_tree_item`, `load_dir_children`, `clear_free_space_cache`, `commit_batch_list`, `do_write`, `free_trees`, `excise_extents`, and rollback helpers.
- Calls dispatch implementations from other files: create/read/write/fileinfo/EA/security/directory/device/PnP/fsctl handlers.
- Calls registry helpers, cache setup, mount-manager helpers, PnP volume notification helpers, balance/scrub/send support, and compression/checksum routines.

## Notable Risks And TODOs

- Transaction log replay is explicitly unimplemented; mount clears `log_tree_addr`.
- Several FIXME comments flag cleanup gaps, including freeing volumes/devpaths on unload, notification uninitialization during unmount, fileref locking/refcount questions, recursion in kernel-mode fileref reaping, subvolume deletion locking, readonly subvolume last-inode handling, and incomplete FS control/object ID handling.
- Compatibility behavior intentionally lies about filesystem type for selected callers, which is important for Windows integration but can surprise diagnostics.
- `mount_vol` generation increments and metadata feature mutation occur before full mount success; error cleanup is broad but not equivalent to full `uninit`.
- `get_file_attributes_from_xattr` accepts non-hex characters by continuing without rejecting them, and uppercase hex branch subtracts `'a'`, which looks suspicious for `A-F`.
