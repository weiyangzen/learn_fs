# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/plugplay.c

This file implements kernel Plug and Play event queuing, device-instance lookup, and the user-mode `NtGetPlugPlayEvent`/`NtPlugPlayControl` interface. It bridges user-mode PnP manager requests to the serialized devaction worker and to device-property/interface helpers.

Event queue:
- `IopInitPlugPlayEvents` initializes `IopPnpEventQueueHead` and `IopPnpNotifyEvent`.
- `IopQueueDeviceChangeEvent`, `IopQueueDeviceInstallEvent`, and `IopQueueTargetDeviceEvent` allocate variable-sized `PNP_EVENT_ENTRY` records, populate `PLUGPLAY_EVENT_BLOCK` payloads, insert at the head of the queue, and signal the notify event.
- `NtGetPlugPlayEvent` requires user mode plus `SeTcbPrivilege`, waits on `IopPnpNotifyEvent`, returns the tail event without removing it, and documents that the function is not multi-thread safe.
- `IopRemovePlugPlayEvent`, called via `PlugPlayControlUserResponse`, removes the tail event and signals the next event if present.

Device lookup and capture:
- `IopFindDeviceInstanceTraverse` compares devnode `InstancePath` values and returns a referenced PDO on match.
- `IopGetDeviceObjectFromDeviceInstance` returns the root PDO for empty/null instance names or traverses from `IopRootDeviceNode` for a matching instance.
- `IopCaptureUnicodeString` safely captures a user `UNICODE_STRING` and its buffer into nonpaged memory with SEH probing.

User-control operations:
- `PiControlInitializeDevice` creates a made-up root device node for a user-supplied instance that does not yet exist: it creates a PnP root PDO, allocates a devnode, duplicates the instance path, sets `DNF_MADEUP`, `DNF_IDS_QUERIED`, and `DNF_ENUMERATED`, writes registry instance data, registers with the root bus, inserts under the root node, and queues `GUID_DEVICE_ENUMERATED`.
- `PiControlSyncDeviceAction` maps `PlugPlayControlEnumerateDevice`, `PlugPlayControlStartDevice`, and `PlugPlayControlResetDevice` to `PiActionEnumDeviceTree`, `PiActionStartDevice`, and `PiActionResetDevice` and calls `PiPerformSyncDeviceAction`.
- `PiControlQueryRemoveDevice` captures and resolves the device instance, but the actual query-remove operation is `STATUS_NOT_IMPLEMENTED`.
- `PiControlDeviceClassAssociation` registers a device interface for a device instance and returns the symbolic link, while unregistering is not implemented.
- `PiControlGetInterfaceDeviceAlias` delegates to `IoGetDeviceInterfaceAlias`.

Query helpers:
- `IopGetInterfaceDeviceList` captures an optional device instance, calls `IoGetDeviceInterfaces`, copies the multi-sz link list to user memory if the buffer is large enough, and returns the required size.
- `IopGetDeviceProperty` handles `PNP_PROPERTY_POWER_DATA` by querying capabilities directly, handles removal-policy hardware default from the devnode, maps many PNP property IDs to `IoGetDeviceProperty`, and marks override/location-path properties as not implemented.
- `IopGetRelatedDevice` returns parent, child, or sibling instance names, with special handling for `HTREE\ROOT\0`.
- `IopGetDeviceNodeStatus` maps devnode state and flags to config-manager `DN_*` status bits.
- `IopDeviceStatus` supports get status/problem, but set and clear are logged as unsupported/FIXME.
- `IopGetDeviceRelations` sends `IRP_MN_QUERY_DEVICE_RELATIONS` for ejection/removal/power/bus relations and returns a double-null-terminated list of related devnode instance paths.
- `IopGetDeviceDepth` returns the devnode `Level`.

System calls:
- `NtPlugPlayControl` requires user mode and `SeTcbPrivilege`, probes the caller buffer, validates minimum buffer sizes per implemented control class, and dispatches to the helpers above.
- Implemented or partially implemented classes include enumerate, initialize, start, reset, user response, get interface list, get property, device class association, get related device, get interface alias, device status, depth, and device relations.
- Many documented classes remain omitted or return `STATUS_NOT_IMPLEMENTED`, including new/deregister device, generate legacy device, target relation, conflict list, dock data, halt device, blocked-driver list, unlock, and query-and-remove internals.

Integration points:
- Consumes tree operations from `devnode.c`.
- Calls `PiPerformSyncDeviceAction` from `devaction.c` for user-triggered enumeration/start/reset.
- Sends direct PnP IRPs through `IopInitiatePnpIrp` for property and relation queries.
- Supplies event notifications consumed by user-mode PnP services.

Research notes:
- The event queue has no visible lock around insert/remove/get and the comment explicitly states `NtGetPlugPlayEvent` is not multi-thread safe.
- `IopGetInterfaceDeviceList` unconditionally calls `ObDereferenceObject(DeviceObject)` after `IoGetDeviceInterfaces`; if no device instance was resolved and `DeviceObject` is NULL, this path depends on dereferencing NULL being harmless, which is unlikely in normal kernel code.
- Several user buffers are probed and then used later after nontrivial work, so the code relies on SEH around final copies for some but not all helper-specific accesses.
