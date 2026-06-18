# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/devaction.c

This file implements the ReactOS kernel PnP manager's serialized device-action pipeline. It owns most device tree mutation: device instance path creation, ID/capability/resource queries, filter and function driver AddDevice ordering, start/enumeration state transitions, resource rebalance stubs, query-remove/remove/eject handling, and the global queued action worker.

Core globals and synchronization:
- `IopDeviceActionRequestList`, `IopDeviceActionWorkItem`, `IopDeviceActionInProgress`, and `IopDeviceActionLock` form the serialized action queue.
- `PiEnumerationFinished` is signaled when the worker drains the queue.
- The file-level comment states the design rule: all device manipulation must flow through `PiQueueDeviceAction` or `PiPerformSyncDeviceAction` to avoid races on the shared device tree.

Device identity and registry initialization:
- `IopValidateID` validates bus-supplied device, instance, hardware, and compatible IDs, enforcing separator limits, printable ASCII, no comma, termination within `MAX_DEVICE_ID_LEN`, and space-to-underscore normalization.
- `IopCreateDeviceInstancePath` sends `IRP_MN_QUERY_ID` for `BusQueryDeviceID` and `BusQueryInstanceID`, sends `IRP_MN_QUERY_CAPABILITIES`, handles non-unique IDs by prepending `IopGetParentIdPrefix`, rejects hardware-disabled devices with `STATUS_PLUGPLAY_NO_DEVICE`, and builds `DeviceID\ParentPrefix&InstanceID`.
- `PiInitializeDevNode` is the main uninitialized-node setup path. It creates the instance path, bugchecks on duplicate instances, creates the enum registry key, queries hardware and compatible IDs, writes text properties, queries bus information, boot resources, and resource requirements, installs critical-device service data, writes service enum data, moves the node to `DeviceNodeInitialized`, and queues a `GUID_DEVICE_ENUMERATED` install event for non-legacy nodes.
- `PiSetDevNodeText` writes `DeviceDesc` if missing and always refreshes `LocationInformation` from `IRP_MN_QUERY_DEVICE_TEXT`, falling back to `"Unknown device"` for missing descriptions.
- `IopSetServiceEnumData` reads the instance `Service` value, duplicates it into `DeviceNode->ServiceName`, opens/creates `Services\<service>\Enum`, writes the device instance at the next numeric slot, and updates `Count` and `NextInstance`.

Driver and filter attachment:
- `PiAttachFilterDriversCallback` resolves a filter or service name under `CurrentControlSet\Services`, rejects disabled services, resolves or loads the driver object when allowed, maps load failures to devnode problems, and appends `ADD_DEV_DRIVERS_LIST` entries.
- `PiAttachFilterDrivers` queries device-level and class-level `LowerFilters` or `UpperFilters` values and tags entries as lower filter, lower class filter, upper filter, or upper class filter.
- `PiCallDriverAddDevice` opens the enum instance key and optional class key, builds the driver call list in Windows-like order: lower filters, lower class filters, function driver, upper filters, upper class filters.
- Function-driver success moves the node to `DeviceNodeDriversAdded`. Failure sets `CM_PROB_FAILED_ADD` and moves to `DeviceNodeAwaitingQueuedRemoval`. Filter AddDevice failures are ignored. RawDeviceOK devices can proceed without a service through a dummy device-driver entry.
- If the resulting attached stack device type is `FILE_DEVICE_ACPI`, the first such node is stored in `PopSystemPowerDeviceNode`.

Capabilities, resources, and start:
- `IopQueryDeviceCapabilities` sends `IRP_MN_QUERY_CAPABILITIES`, maps WDM capability bits into config-manager `CapabilityFlags`, updates `DNUF_DONT_SHOW_IN_UI`, and writes `Capabilities` plus `UINumber` to the instance registry key.
- `IopQueryHardwareIds` and `IopQueryCompatibleIds` send `IRP_MN_QUERY_ID` and write `HardwareID`/`CompatibleIDs` REG_MULTI_SZ values.
- `PiStartDeviceFinal` ensures reported devices have IDs queried, sets `DNF_REENUMERATE`, refreshes capabilities after start, queries PnP device state, queues `GUID_DEVICE_ARRIVAL`, and moves to `DeviceNodeStarted`.
- `PiUpdateDeviceState` sends `IRP_MN_QUERY_PNP_DEVICE_STATE`, updates user-visible flags, maps removed/disabled/failed states to devnode problems and queued removal, and handles resource-requirements-changed by setting `DNF_RESOURCE_REQUIREMENTS_CHANGED` and optionally `DNF_NON_STOPPED_REBALANCE`.
- `PiFakeResourceRebalance` is a placeholder rebalance path: it re-queries boot resources and resource requirements and clears `DNF_RESOURCE_REQUIREMENTS_CHANGED`.

Enumeration and state machine:
- `PiEnumerateDevice` consumes `DeviceNode->OverUsed1.PendingDeviceRelations` from a BusRelations query, marks existing children non-enumerated, creates `DEVICE_NODE`s for new PDOs with `PipAllocateDeviceNode` and `PiInsertDevNode`, marks returned existing children enumerated, and marks missing children as gone/awaiting removal.
- `PiDevNodeStateMachine` traverses the devnode subtree, takes a temporary PDO reference for traversal stability, skips problem nodes unless they are awaiting removal, and advances states synchronously:
  - `DeviceNodeUninitialized` -> `PiInitializeDevNode`
  - `DeviceNodeInitialized` -> `PiCallDriverAddDevice`
  - `DeviceNodeDriversAdded` -> `IopAssignDeviceResources`
  - `DeviceNodeResourcesAssigned` -> `PiIrpStartDevice`
  - `DeviceNodeStartCompletion` -> success post-work or failed-start problem/removal
  - `DeviceNodeStartPostWork` -> `PiStartDeviceFinal`
  - started reenumeration -> `PiIrpQueryDeviceRelations` and `PiEnumerateDevice`
  - resource changes -> query-stop/stop/fake rebalance/re-add-driver loop
  - awaiting removal -> `IopRemoveDevice`

Removal and eject:
- `PiIrpSendRemoveCheckVpb` sends query/cancel/surprise/remove IRPs, walking attached devices to locate mounted VPBs and toggling `VPB_REMOVE_PENDING` to block mounts on devices being removed.
- `IopPrepareDeviceForRemoval` enforces `DNUF_NOT_DISABLEABLE` unless forced, sends query-remove unless forced, recursively queries/removes `RemovalRelations` and child devices, and sends cancel-remove on failures.
- `IopRemoveDevice` uses forced behavior for `DNF_DEVICE_GONE` surprise removal, sends surprise-removal notification/events when applicable, then sends remove and safe-removal events on success.
- `IopSendRemoveDevice` sends `IRP_MN_REMOVE_DEVICE`, clears stored resource lists for registry conflict-detection compatibility, moves to `DeviceNodeRemoved`, notifies `GUID_TARGET_DEVICE_REMOVE_COMPLETE`, and dereferences the PDO while logging leaks.
- `IoRequestDeviceEject` queues kernel-initiated eject, queries ejection relations and child removal, prepares the target, sends removal to relations/children, sets `CM_PROB_HELD_FOR_EJECT`, optionally sends `IRP_MN_EJECT`, and queues eject or eject-vetoed events.

Action queue API:
- `PipDeviceActionWorker` drains queued `DEVICE_ACTION_REQUEST`s and dispatches `PiActionAddBootDevices`, `PiActionEnumRootDevices`, `PiActionEnumDeviceTree`, `PiActionResetDevice`, `PiActionStartDevice`, and `PiActionQueryState`.
- `PiQueueDeviceAction` allocates a nonpaged request, references the target device, enqueues under the action spin lock, runs root enumeration/add-boot actions synchronously, defers normal work until boot drivers are loaded, and otherwise queues `PipDeviceActionWorker` to `DelayedWorkQueue`.
- `PiPerformSyncDeviceAction` wraps the queue path with a local event and returns the worker-computed status.

Integration points:
- Uses `devnode.c` for node allocation, insertion, state, and problem flags.
- Uses `pnpirp.c` helpers for synchronous PnP IRPs.
- Uses registry helpers and resource assignment/update paths elsewhere in the kernel.
- Emits user-mode and target-device events through `plugplay.c` helpers.

Research notes:
- The state names include pending states, but this implementation usually performs PnP IRPs synchronously and then manually skips through completion states.
- Removal code comments acknowledge the subtree removal implementation is currently concentrated in `IopRemoveDevice` and should be a separate removal worker with more precise state transitions.
- Several TODO/FIXME areas remain: critical cleanup for ID/capability failures, proper resource rebalance, deferred interface-state work, legacy driver AddDevice behavior, class property import, and stronger invalid-ID handling.
- `PiUpdateDeviceState` appears suspicious in the resource-requirements-changed branch: `DeviceNode->Flags &= DNF_NON_STOPPED_REBALANCE` when `PNP_DEVICE_FAILED` is set clears all flags except that bit, likely intended to clear only `DNF_NON_STOPPED_REBALANCE`.
- Registry and object lifetime handling is delicate: driver-object references from service/filter resolution, relation PDO references, VPB lock ordering, and devnode removal references must remain balanced.
