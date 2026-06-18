# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpinit.c

This file initializes core PnP manager state during kernel startup: arbiter instances, service group ordering caches, enum/root registry keys, the PnP root driver/PDO/devnode, event notification, bus-type GUID storage, root enumeration, and firmware mapping.

Globals:
- `PiInitGroupOrderTable` and `PiInitGroupOrderTableCount` cache `ServiceGroupOrder\List`.
- `PnpDefaultInterfaceType` is currently `Isa`.
- `PnPBootDriversLoaded` and `PnPBootDriversInitialized` gate device action processing and driver loading in `devaction.c`.
- Root arbiters are declared for bus numbers, IRQ, DMA, memory, and ports.

Initialization helpers:
- `IopDetermineDefaultInterfaceType` returns `Isa` with a FIXME for MicroChannel support.
- `IopInitializeArbiters` initializes port, memory, DMA, IRQ, and bus-number arbiters in order, failing fast on errors.
- `PiInitCacheGroupInformation` reads `CurrentControlSet\Control\ServiceGroupOrder\List`, validates REG_MULTI_SZ, converts it to an array of `UNICODE_STRING`s, and caches it.
- `PpInitGetGroupOrderIndex` returns a service's group index in the cached group table, the end/default index when no group exists, or count+1 when called with no service handle.
- `PipGetDriverTagPriority` reads a service's `Group` and `Tag`, then looks up that group's tag-order binary list under `ServiceGroupOrder` to return the tag priority index.

Main startup path:
- `IopInitializePlugPlayServices` initializes tree/action locks and request list, sets `PiEnumerationFinished`, determines the default interface type, initializes arbiters, and caches group ordering.
- It opens/creates `CurrentControlSet\Control`, `Control\DeviceClasses`, `Enum`, `Enum\Root`, and the root devnode registry key.
- It creates the root PnP manager driver via `IoCreateDriver(PnpRootDriverEntry)`, creates the root PDO, marks it bus-enumerated, allocates `IopRootDeviceNode`, sets `DNF_MADEUP`, `DNF_ENUMERATED`, `DNF_IDS_QUERIED`, and `DNF_NO_RESOURCE_REQUIRED`, creates the root instance path, initializes the root extension, and marks the root node started.
- It initializes Plug and Play events with `IopInitPlugPlayEvents`.
- It initializes `PnpBusTypeGuidList` with capacity for eight GUIDs.
- It queues root enumeration synchronously with `PiQueueDeviceAction(PiActionEnumRootDevices)`, calls `IopUpdateRootKey` to map firmware-detected devices into Enum\Root, closes the control-set handle, and queues root enumeration again.

Integration points:
- Sets up globals consumed by `devnode.c`, `devaction.c`, `plugplay.c`, and bus-type GUID management.
- Calls firmware mapping from `pnpmap.c`.
- Boot driver flags defined here control whether `PiQueueDeviceAction` starts asynchronous work and whether `PiCallDriverAddDevice` may load missing drivers.

Research notes:
- Several error paths in `IopInitializePlugPlayServices` return without closing handles opened earlier, which may be acceptable during phase-1 init failure but is still worth noting.
- Root enumeration is intentionally run twice: once before firmware mapping and once after `IopUpdateRootKey` creates firmware-backed root enum entries.
- Service group and tag order routines assume registry value types/data are valid in places through `ASSERT`s rather than graceful validation.
