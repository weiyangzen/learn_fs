# File Research: sources/windows/winbtrfs/src/boot.c

## Purpose

`boot.c` contains WinBtrfs boot-volume discovery and early boot-device registration support. It identifies whether `\SystemRoot` points to a Btrfs ARC path, extracts the boot filesystem UUID, parses a boot subvolume option, and forces device registration/notifications so the Windows boot volume is available early enough.

## Global State

- `BTRFS_UUID boot_uuid`
  - Boot filesystem UUID parsed from `\SystemRoot` / `\Device\BootDevice` symbolic link targets.
- `uint64_t boot_subvol`
  - Optional boot subvolume ID parsed from `SystemStartOptions`.

## Boot Root Discovery

`get_system_root()`:

- Opens the `\SystemRoot` symbolic link.
- Queries the link target length, allocates a buffer, and reads the target.
- If `\SystemRoot` points at `\Device\BootDevice`, follows that symbolic link too.
- Logs the discovered target.
- Checks for an ARC path prefix `\ArcName\btrfs(`.
- Parses a UUID in text form from the path:
  - two hex digits per byte
  - hyphens after UUID byte indexes 3, 5, 7, and 9
  - closing `)` after the UUID
- Stores the result in `boot_uuid`.
- Returns `true` only for a valid Btrfs ARC boot path.

## Mount Manager Notification

`mountmgr_notification(BTRFS_UUID* uuid)`:

- Opens the mount manager device.
- Builds a `MOUNTMGR_TARGET_NAME` using `BTRFS_VOLUME_PREFIX` plus the UUID text form.
- Sends `IOCTL_MOUNTMGR_VOLUME_ARRIVAL_NOTIFICATION`.
- Frees the allocated target-name buffer.

This is used after forcibly adding a boot device so mount manager sees the Btrfs volume arrival.

## Boot Options

`check_boot_options()`:

- Opens `\Registry\Machine\SYSTEM\CurrentControlSet\Control`.
- Queries `SystemStartOptions`.
- Searches for `SUBVOL=`.
- Parses following hex digits into `boot_subvol`.
- Logs the parsed subvolume when nonzero.
- Uses structured exception handling around registry/string access.

## Device Addition

`boot_add_device(DEVICE_OBJECT* pdo)`:

- Calls `AddDevice(drvobj, pdo)` manually for the target PDO.
- Sets `pdode->dont_report = true`.
- Clears `DOE_START_PENDING` on the PDO’s `DeviceObjectExtension`.
- If the volume child device exists, clears `DOE_START_PENDING` on it too.
- Calls `mountmgr_notification()` for the volume UUID.

The explicit `DOE_START_PENDING` clearing is there because early boot code may need `NtOpenFile` to succeed before normal PnP relation reporting finishes.

## Public Boot Check

`check_system_root()`:

- Waits for any in-progress boot PnP notification by acquiring and releasing `boot_lock`.
- Calls `get_system_root()`.
- Scans global `pdo_list` under `pdo_list_lock` for a PDO whose UUID matches `boot_uuid`.
- If the PDO has no volume device extension yet, saves it for manual `boot_add_device()`.
- If `AddDevice` already ran, marks both the child device and PDO with `DO_SYSTEM_BOOT_PARTITION`.
- Toggles the bus device interface off and on so Windows reobserves the boot partition state.
- Releases `pdo_list_lock`.
- Parses boot options.
- Calls `boot_add_device()` when a matching PDO must be added manually.

## Important Dependencies

- External globals:
  - `pdo_list_lock`
  - `pdo_list`
  - `boot_lock`
  - `drvobj`
- Driver helpers/macros:
  - `AddDevice`
  - `dev_ioctl`
  - `hex_digit`
  - `mountmgr_add_drive_letter` indirectly through nearby device flows
  - `BTRFS_VOLUME_PREFIX`
- Windows kernel APIs:
  - `ZwOpenSymbolicLinkObject`
  - `ZwQuerySymbolicLinkObject`
  - `ZwOpenKey`
  - `ZwQueryValueKey`
  - `IoGetDeviceObjectPointer`
  - `IoSetDeviceInterfaceState`
  - `ExAcquireResource*`
  - `ExAllocatePoolWithTag`
  - `ExFreePool`

## Notable Details

- `DEVOBJ_EXTENSION2` is a local partial definition used only to reach `ExtensionFlags` and clear `DOE_START_PENDING`.
- `check_boot_options()` has FIXME comments:
  - it uses a fixed 255-WCHAR buffer and should not fail for longer values;
  - it writes a terminator at `options[DataLength / sizeof(WCHAR)]` and notes the buffer-size assumption.
- `mountmgr_notification()` returns without dereferencing `FileObject` if allocation of `mmtn` fails, which appears to leak the mount manager file object on that path.
- `boot_add_device()` dereferences `pdode` before verifying it is non-null; expected callers pass WinBtrfs PDOs.
- The UUID parser is strict about hex digits, hyphen positions, and closing parenthesis, and returns false on malformed paths.
