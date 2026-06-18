# File Research: sources/windows/reactos/drivers/filesystems/btrfs/boot.c

Implements Btrfs boot-volume discovery and boot-time device attachment support for ReactOS/Windows-style kernel boot.

Key entry points:
- `check_system_root()` resolves `\SystemRoot` and, if necessary, `\Device\BootDevice`, parses a Btrfs ARC-style boot UUID, finds the matching pending PDO, marks an already-added device as a system boot partition or calls `boot_add_device()`, and parses boot subvolume options.
- `boot_add_device()` calls the driver's `AddDevice()`, suppresses pending-device reporting, clears `DOE_START_PENDING` on the PDO and mounted device extension, and sends a mount-manager arrival notification.
- `get_system_root()` reads kernel symbolic links to identify whether the boot path is `\ArcName\btrfs(<uuid>)`, then decodes the UUID into global `boot_uuid`.
- `check_boot_options()` reads `SystemStartOptions` from the registry and parses a hexadecimal `SUBVOL=` value into global `boot_subvol`.
- `mountmgr_notification()` constructs a Btrfs volume target name from a UUID and sends `IOCTL_MOUNTMGR_VOLUME_ARRIVAL_NOTIFICATION`.

Core mechanics:
- Uses global boot state `boot_uuid` and `boot_subvol`.
- Uses `pdo_list_lock` and `boot_lock` to coordinate with PnP discovery.
- Handles systems where normal PnP relation callbacks happen too late for a filesystem needed as the boot volume.
- Toggles the device interface state when `AddDevice()` already ran but the mounted device was not marked as `DO_SYSTEM_BOOT_PARTITION`.
- Uses SEH around registry boot-option parsing to tolerate malformed or inaccessible data.

Important invariants:
- The ARC Btrfs path parser expects exactly a UUID in canonical 8-4-4-4-12 hex form inside `\ArcName\btrfs(...)`.
- Mount-manager target names use `BTRFS_VOLUME_PREFIX` plus the formatted UUID and closing brace.
- The `DOE_START_PENDING` bits are cleared because boot-time `NtOpenFile` can otherwise see `STATUS_NO_SUCH_DEVICE`.
- `check_system_root()` waits for any active boot PnP notification before scanning the PDO list.

Filesystem/boot relevance:
- This file lets the Btrfs driver participate in system boot by identifying the boot Btrfs volume early enough, attaching the driver stack manually when needed, and carrying a requested boot subvolume into mount logic.

Notable risks:
- `mountmgr_notification()` leaks the referenced mount-manager file object if allocation of the notification buffer fails before `ObDereferenceObject(FileObject)`.
- `check_boot_options()` writes a trailing NUL at `options[kvfi->DataLength / sizeof(WCHAR)]` inside a fixed-size query buffer; the comment acknowledges that buffer space should be verified.
- The boot subvolume parser shifts by 4 and accepts only hex digits, so decimal-looking `SUBVOL=` values are interpreted as hexadecimal.
- `get_system_root()` is strict about the ARC path format and returns false for any deviation.
