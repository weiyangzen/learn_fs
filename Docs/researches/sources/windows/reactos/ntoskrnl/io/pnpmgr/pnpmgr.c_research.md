# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpmgr.c

Read status: complete file, 1857 lines.

This file provides central PnP manager support routines: device-instance registry helpers, critical-device database matching, bus-type GUID indexing, synchronous PnP IRP construction, device property lookup, resource-list sizing, and exported PnP-facing kernel APIs.

Key entry points:
- `IopInstallCriticalDevice()` reads a device instance's `HardwareID` and optional `CompatibleIDs`, normalizes backslashes to `#`, scans `CriticalDeviceDatabase`, and copies matching `ClassGUID` and optional `Service` values into the Enum instance key.
- `IopGetBusTypeGuidIndex()` maintains the global `PnpBusTypeGuidList`, growing it in blocks of eight GUIDs under a fast mutex.
- `IopInitiatePnpIrp()` builds a temporary `IRP_MJ_PNP` stack location and delegates to `IopSynchronousCall()`.
- `IopCreateDeviceKeyPath()` creates nested device instance registry keys under `Enum`, while `IopCreateRegistryKeyEx()` is a more generic nested key creator.
- `IopSetDeviceInstanceData()` creates `LogConf`, `Control`, and ACPI `Device Parameters` registry data, writing boot resources, resource requirements, default `ConfigFlags`, and `FirmwareIdentified`.
- `IopGetParentIdPrefix()` retrieves or generates a parent ID prefix from the parent's instance path and CRC32, then stores it in the parent Enum key.
- `PnpBusTypeGuidGet()`, `PnpDeviceObjectToDeviceInstance()`, `PnpDetermineResourceListSize()`, `PiGetDeviceRegistryProperty()`, `IoGetDeviceProperty()`, `IoOpenDeviceRegistryKey()`, `IoInvalidateDeviceRelations()`, `IoSynchronousInvalidateDeviceRelations()`, `IoTranslateBusAddress()`, and `IoInvalidateDeviceState()` expose the implemented property, registry, relation, and translation surface.
- `PiInitPhase0()` initializes `PpRegistryDeviceResource` and the device-reference AVL table; `PpInitSystem()` dispatches PnP manager initialization by kernel phase.

Important dependencies:
- Registry APIs: `ZwOpenKey`, `ZwCreateKey`, `ZwQueryValueKey`, `ZwSetValueKey`, `ZwEnumerateKey`, `RtlQueryRegistryValues`.
- Device-node state: `IopGetDeviceNode`, `IopIsValidPhysicalDeviceObject`, `IopRootDeviceNode`, `PopSystemPowerDeviceNode`, `IopDeviceTreeLock`.
- PnP action queue: `PiQueueDeviceAction`, `PiPerformSyncDeviceAction`.
- Resource support: `PnpDetermineResourceListSize`, `PnpBusTypeGuidList`, HAL address translation.

Notable behavior and risks:
- The device-reference AVL table is initialized with compare/allocate/free callbacks that assert false and return dummy values, so it is a placeholder rather than usable storage.
- `IopInstallCriticalDevice()` has several early-continue paths after opening or allocating nested critical-device data that do not consistently close/free all intermediate objects.
- `IoGetDeviceProperty()` implements common bus, identifier, name, removal-policy, and registry-backed properties, but resource requirements, allocated resources, and container ID are explicitly unimplemented.
- `IoOpenDeviceRegistryKey()` requires a valid PDO, builds either driver class-key or Enum device-key paths, and creates the `Device Parameters` subkey for device keys.
- Device-relation invalidation only acts on `BusRelations`; synchronous invalidation returns `STATUS_NOT_IMPLEMENTED` for `PowerRelations` and success/no-op for `TargetDeviceRelation`.
