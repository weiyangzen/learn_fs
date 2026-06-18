# File Research: sources/local-fs/ntfs-3g/libntfs-3g/volume.c

Implements NTFS volume allocation, startup, mounting, unmounting, mount-state checks, logfile/hibernation safety checks, volume flag updates, free-space accounting, locale setup, mount error classification, and volume label changes.

`ntfs_volume_startup()` is the low-level mount bootstrap. It allocates an `ntfs_volume`, builds the default upcase table, initializes visibility/compression/case flags, opens the device read-write or read-only, reads and validates the boot sector, parses geometry, configures the device block size, initializes cluster allocator zones, loads `$MFT`, and loads `$MFTMirr`.

`ntfs_mft_load()` manually creates the `$MFT` inode before ordinary inode access is available. It reads the first MFT record with MST protection, validates it, optionally reads `$ATTRIBUTE_LIST`, opens `$MFT/$DATA`, decompresses and merges all mapping-pair extents, verifies the runlist begins at the boot-sector MFT LCN, updates inode size fields, and opens `$MFT/$BITMAP`. `ntfs_mftmirr_load()` opens `$MFTMirr/$DATA`, maps its runlist, and verifies its first LCN matches the boot-sector mirror LCN.

`ntfs_device_mount()` completes the full library mount. It compares `$MFTMirr` against the initial `$MFT` records, validates MST records, loads `$Bitmap`, loads and checks `$UpCase`, opens `$Volume`, reads `$VOLUME_INFORMATION` and optional `$VOLUME_NAME`, loads `$AttrDef`, opens `$Secure`, and checks unsafe Windows states for read-write mounts. It rejects hibernated/fast-restart volumes, can fall back to read-only when requested, can reset an unclean logfile if recovery is enabled, and calls `fix_txf_data()` to make root `$TXF_DATA` resident for Windows compatibility.

Hibernation detection opens `/hiberfil.sys`, reads the first 4096 bytes, and treats short reads or `hibr`/`HIBR` signatures as unsafe. Logfile checking opens `$LogFile`, parses restart pages through `ntfs_check_logfile()`/`ntfs_is_logfile_clean()`, and rejects version 2.0 cached metadata as `EPERM`.

Other exported helpers include `ntfs_mount()`, `ntfs_umount()`, `ntfs_set_shown_files()`, `ntfs_set_ignore_case()`, `ntfs_check_if_mounted()`, `ntfs_version_is_supported()`, `ntfs_logfile_reset()`, `ntfs_volume_write_flags()`, `ntfs_volume_error()`, `ntfs_mount_error()`, `ntfs_set_locale()`, `ntfs_volume_get_free_space()`, and `ntfs_volume_rename()`.

Dependencies are broad: boot-sector parsing, MFT/inode/attribute APIs, runlists, MST fixups, logfile parsing, directory lookup, Unicode conversion, secure metadata, cache management, device operations, mount table APIs, and NTFS logging. Key invariants are that core system files must be loaded in mount-order, `$MFT` and `$MFTMirr` must match for protected records, `$UpCase` must have sane size and ASCII mappings, `$VOLUME_INFORMATION` and `$VOLUME_NAME` must be resident, and read-write mounts are denied unless hibernation/logfile state is safe or explicitly recoverable.
