# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/devctl.c

This file implements Ext2Fsd device-control dispatch for app-facing IOCTLs and pass-through device IOCTLs. It handles volume/global property control, performance-stat queries, DOS mount-point symbolic links, and optional driver unload preparation.

Key responsibilities:
- Dispatch `IRP_MJ_DEVICE_CONTROL` requests by IOCTL code.
- Forward unrecognized device controls to the mounted volume's lower storage device.
- Apply or query global and per-volume Ext2Fsd properties.
- Expose driver version/build strings and performance counters.
- Add/delete `\DosDevices\Global\X:` symbolic links for mount points.
- Optionally transition the driver into an unload-ready state.

Important functions:
- `Ext2DeviceControl`: Top-level IOCTL switch for `IOCTL_APP_VOLUME_PROPERTY`, `IOCTL_APP_QUERY_PERFSTAT`, `IOCTL_APP_MOUNT_POINT`, optional `IOCTL_PREPARE_TO_UNLOAD`, and lower-driver forwarding.
- `Ext2DeviceControlNormal`: Validates the request is for a volume, copies the stack location to the next IRP stack slot, installs `Ext2DeviceControlCompletion`, and calls the target device.
- `Ext2ProcessGlobalProperty`: Handles global read/write policy, ext3 force-write policy, automount, hiding prefix/suffix patterns, codepage loading, and version query.
- `Ext2ProcessVolumeProperty`: Handles per-volume readonly/ext3-writable state, journal recovery attempt, hiding rules, drive letter, user id overrides, UUID, codepage, and automount query/set state.
- `Ext2ProcessUserProperty`: Validates property magic, routes requests to global versus volume property processors, and returns the full property buffer length on success.
- `Ex2ProcessUserPerfStat`: Returns global performance counters in v1 or v2 layout after validating magic, command, and buffer size.
- `Ex2ProcessMountPoint`: Creates or deletes a DOS-device symlink for a requested drive letter.
- `Ext2PrepareToUnload`: Under `EXT2_UNLOAD`, removes dismounted VCBs, refuses unload if mounted volumes remain, unregisters file-system devices, and sets `EXT2_UNLOAD_PENDING`.

Important interactions:
- Uses `Ext2Global->Resource` for global property/unload serialization and `Vcb->MainResource` for per-volume property changes.
- Calls `Ext2FlushFiles`, `Ext2FlushVolume`, and `Ext2RecoverJournal` when changing volume writability.
- Uses NLS `load_nls` to install global or volume codepage tables.
- Completes requests through `Ext2CompleteIrpContext`, except forwarded IOCTLs detach the IRP from the context.

Notable behavior and risks:
- Several property switch cases intentionally fall through from v3 to v2 to v1 handling.
- The ReactOS-specific code changes some original assignment-in-condition patterns for hiding flags into comparisons, which may alter upstream Ext2Fsd behavior.
- Per-volume codepage assignment stores the table pointer even if `load_nls` fails; label initialization is gated on a non-null page table.
- `Ex2ProcessMountPoint` trusts a single drive-letter character and constructs only `\DosDevices\Global\Z:`-style links.
