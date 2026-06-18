# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnproot.c

Read status: complete file, 1529 lines.

This file implements the root PnP bus driver and root-enumerated PDO handling. It keeps an in-memory list of root devices, creates PDOs for registry-backed and legacy-reported devices, answers PnP IRPs for those PDOs, and exposes the root driver's dispatch entry points.

Key entry points:
- `PnpRootInitializeDevExtension()` initializes the static root FDO extension list and lock.
- `PnpRootCreateDeviceObject()` creates unnamed root-child PDOs with `PNPROOT_PDO_DEVICE_EXTENSION`.
- `PnpRootCreateDevice()` creates a new `Root\\<service>\\NNNN` legacy/root device, updates the registry `NextInstance`, creates the instance key, creates a PDO, and links it into the root list.
- `PnpRootRegisterDevice()` registers an externally supplied PDO by splitting its instance path into device ID and instance ID, then links it into the root list.
- `EnumerateDevices()` walks `HKLM\\System\\CurrentControlSet\\Enum\\Root`, skips `LEGACY_` keys, filters unreported devices, and calls `CreateDeviceFromRegistry()` for each accepted instance.
- `PnpRootQueryDeviceRelations()` enumerates devices, creates missing PDOs, references them, merges any incoming relations, and returns a `DEVICE_RELATIONS` list.
- `PnpRootFdoPnpControl()` handles root FDO `IRP_MN_QUERY_DEVICE_RELATIONS`.
- `PnpRootPdoPnpControl()` handles child PDO PnP minors including start, target relation, capabilities, resources, resource requirements, text, IDs, bus information, and remove.
- `PnpRootPowerControl()` trivially succeeds query/set power IRPs.
- `PnpRootDriverEntry()` records `IopRootDriverObject`, installs PnP/power dispatch routines, and optionally creates a PFN dump device when tracing is enabled.

Important dependencies:
- Registry helpers: `IopOpenRegistryKeyEx`, `RtlQueryRegistryValues`, `ZwEnumerateKey`, `ZwCreateKey`.
- PnP manager device-node ownership: `IopGetDeviceNode`, `IopRootDeviceNode`.
- Device object lifecycle: `IoCreateDevice`, `IoDeleteDevice`, `ObReferenceObject`.
- Root enum constants: `REGSTR_PATH_SYSTEMENUM`, `REGSTR_KEY_ROOTENUM`.

Notable behavior and risks:
- Root device state is global/static (`PnpRootDOExtension`) rather than attached to a normal FDO device extension.
- `IopShouldProcessDevice()` only asserts `DeviceReported == 1`; it does not reject other DWORD values after reading them.
- `PnpRootCreateDevice()` allocates `FullInstancePath->MaximumLength` without explicit room for a terminating null, matching `UNICODE_STRING` length use but risky for callers treating it as null-terminated.
- PDO remove frees strings and resource buffers, unlinks the device, frees `DeviceInfo`, and deletes the PDO.
- `PdoQueryCapabilities()` only sets `UniqueID = TRUE`; most capability fields remain caller-initialized.
- Hardware and compatible ID queries are optional no-ops for root PDOs, while device ID and instance ID are duplicated from `PNPROOT_DEVICE`.
