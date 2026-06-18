# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/deviface.c

This file implements Plug and Play device-interface registration, lookup, aliasing, enumeration, registry-key access, and interface enable/disable notifications.

Key behavior:
- Device interface symbolic links use either kernel `\??\` or user `\\?\` prefixes and encode device instance paths by replacing backslashes with `#`, followed by the interface class GUID and optional reference string.
- `IopBuildSymbolicLink` constructs symbolic links from a device instance string, GUID string, optional reference string, and prefix mode.
- `IopSeparateSymbolicLink` parses a link into prefix, munged device string, GUID string, optional reference string, and optional GUID value.
- Registry state is stored below `HKLM\System\CurrentControlSet\Control\DeviceClasses\{GUID}` using munged symbolic-link device keys and reference-string instance subkeys.
- `IoRegisterDeviceInterface` validates the PDO and reference string, creates the class/device/reference registry keys, writes `DeviceInstance` and `SymbolicLink`, creates the kernel symbolic link to the PDO object name, and returns the interface symbolic link.
- `IoGetDeviceInterfaces` enumerates class keys, optionally filters by a specific PDO `InstancePath`, skips `Control`, optionally filters inactive interfaces via `Control\Linked`, reads `SymbolicLink`, normalizes its prefix to `\??\`, and returns a double-null-terminated list.
- `IoOpenDeviceInterfaceRegistryKey` opens or creates the per-interface `Device Parameters` key.
- `IoGetDeviceInterfaceAlias` uses the existing interface’s `DeviceInstance` and reference string with another class GUID, then verifies the alias instance key exists.
- `IoSetDeviceInterfaceState` writes volatile `Control\Linked`, reconstructs the device instance from the symbolic link, resolves the PDO, and sends arrival/removal notifications through `PiNotifyDeviceInterfaceChange` and `IopQueueDeviceChangeEvent`.

Integration points:
- Shares `IopGetDeviceObjectFromDeviceInstance` with driver-loading code.
- Uses registry helper APIs such as `IopOpenRegistryKeyEx`, `IopCreateRegistryKeyEx`, `IopGetRegistryValue`, and PnP registry string conversion.
- Emits PnP/device-change events consumed by the wider kernel PnP notification path.
- Creates symbolic links through `IoCreateSymbolicLink` and updates existing links on collision.

Research notes:
- Several paths manually duplicate symbolic-link parsing and munging instead of always using the helper, so format changes would need careful synchronization.
- `IopBuildSymbolicLink` duplicates the munged device string but does not free it in the visible success or failure paths after allocation.
- `IopOpenOrCreateSymbolicLinkSubKeys` can call `ZwDeleteKey(DeviceKeyHandle)` on failure when `Create` is true before confirming the handle is non-NULL.
- `IoGetDeviceInterfaces` has cleanup-sensitive `continue` paths while filtering by PDO that can skip closing/freeing the current device-key state.
- `IoRegisterDeviceInterface` contains multiple early-return error paths after allocations or key opens; the visible code does not consistently free the GUID string from `RtlStringFromGUID` or close/free all intermediate resources.
- Enabling/disabling an interface changes registry state and sends notifications; the symbolic link itself is created during registration and is not deleted on disable in this file.
