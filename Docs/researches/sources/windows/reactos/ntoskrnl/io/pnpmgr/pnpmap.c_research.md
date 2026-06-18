# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpmap.c

This file implements the boot-time firmware mapper that creates Enum\Root entries from firmware-detected devices under `HARDWARE\DESCRIPTION\System\MultifunctionAdapter`.

Mapping data:
- Static registry value names cover `Identifier`, `HardwareID`, `Configuration Data`, `BootConfig`, and `LogConf`.
- `KeyboardMap` maps firmware keyboard identifiers to PNP keyboard IDs.
- `PointerMap` maps firmware mouse/pointer identifiers to PNP pointer IDs.
- `PnPMap` maps detected firmware path names such as `SerialController`, `KeyboardPeripheral`, `PointerPeripheral`, `ParallelController`, and `FloppyDiskPeripheral` to direct PNP IDs or peripheral submaps, with a per-map `Counter` used for instance numbering.

Mapping helpers:
- `IopMapPeripheralId` compares a firmware identifier value against a peripheral submap and returns the matching PNP ID.
- `IopMapDetectedDeviceId` matches the detected key path against `PnPMap`, increments and returns the instance index, and delegates to a peripheral map when needed.

Firmware enumeration:
- `IopEnumerateDetectedDevices` recursively walks firmware registry keys, optionally opening relative paths and optionally recursing through subkeys.
- It reads `Configuration Data` as `REG_FULL_RESOURCE_DESCRIPTOR`, concatenating child and parent boot resources so child devices inherit parent descriptors.
- It reads optional `Identifier`, maps the detected path/value to a PNP hardware ID, creates `Enum\Root\<HardwareId>\<Instance>` keys, writes `HardwareID` as REG_MULTI_SZ, creates volatile `LogConf`, and writes `BootConfig` as REG_RESOURCE_LIST when boot resources are available.
- The function dynamically resizes key/value query buffers on `STATUS_BUFFER_OVERFLOW`/`STATUS_BUFFER_TOO_SMALL` and cleans up per-device handles, temporary boot-resource buffers, and value buffers in the loop.

Enable/disable and entry point:
- `IopIsFirmwareMapperDisabled` reads `CurrentControlSet\Control\Pnp\DisableFirmwareMapper`; nonzero disables enumeration.
- `IopUpdateRootKey` ensures `Enum` and `Enum\Root` exist, skips mapping when disabled, opens `HARDWARE\DESCRIPTION\System\MultifunctionAdapter`, and calls `IopEnumerateDetectedDevices`. Missing firmware keys are treated as success/no work.

Integration points:
- Called by `IopInitializePlugPlayServices` between two root enumeration passes.
- The generated Enum\Root keys are later visible to the PnP root enumerator and devaction initialization/start paths.

Research notes:
- The file comments state the trailing null characters embedded in static PNP IDs are hacks and that INF `LegacyXlate` sections should also be considered.
- Resource concatenation is careful about `CmResourceTypeDeviceSpecific` ordering but is complex and easy to regress.
- `IopIsFirmwareMapperDisabled` reads the registry DWORD with `(ULONG)(*KeyInformation->Data)`, effectively only reading the first byte of the data buffer rather than a full `ULONG`.
- In one allocation-failure branch after resizing the `Configuration Data` buffer, the code calls `ZwDeleteKey(hLevel2Key)` before `hLevel2Key` is initialized in that loop scope.
