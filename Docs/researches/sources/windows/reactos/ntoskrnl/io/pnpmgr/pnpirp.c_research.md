# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpirp.c

This file centralizes synchronous sending of common `IRP_MJ_PNP` requests and provides typed wrappers used by the PnP state machine.

Core IRP sender:
- `IopSynchronousCall` references the top attached device, allocates an IRP with that stack size, initializes `IoStatus` to `STATUS_NOT_SUPPORTED`, sets up a synchronization event and user IOSB, queues the IRP to the current thread, copies in the supplied stack location, calls the driver, waits for `STATUS_PENDING`, dereferences the top device, and returns `IoStatusBlock.Information` through an out pointer.
- It has a special case for `IRP_MN_FILTER_RESOURCE_REQUIREMENTS`, seeding the IRP information field from the filter-resource-requirements list before the call.

PnP request wrappers:
- `PiIrpStartDevice` sends `IRP_MN_START_DEVICE` with assigned raw and translated resource lists, requires `DeviceNodeResourcesAssigned`, and stores completion status.
- `PiIrpStopDevice` sends `IRP_MN_STOP_DEVICE`, requires `DeviceNodeQueryStopped`, and asserts success.
- `PiIrpQueryStopDevice` sends `IRP_MN_QUERY_STOP_DEVICE`, requires `DeviceNodeStarted`, and stores completion status.
- `PiIrpCancelStopDevice` sends `IRP_MN_CANCEL_STOP_DEVICE`, requires `DeviceNodeQueryStopped`, and asserts success while ignoring the returned status semantically.
- `PiIrpQueryDeviceRelations` sends `IRP_MN_QUERY_DEVICE_RELATIONS`, requires `DeviceNodeStarted`, stores returned relations in `DeviceNode->OverUsed1.PendingDeviceRelations`, and stores completion status.
- `PiIrpQueryResources` sends `IRP_MN_QUERY_RESOURCES` and returns a `CM_RESOURCE_LIST`.
- `PiIrpQueryResourceRequirements` sends `IRP_MN_QUERY_RESOURCE_REQUIREMENTS` and returns an `IO_RESOURCE_REQUIREMENTS_LIST`.
- `PiIrpQueryDeviceText` sends `IRP_MN_QUERY_DEVICE_TEXT`, requires `DeviceNodeUninitialized`, and returns a driver-allocated text string.
- `PiIrpQueryPnPDeviceState` sends `IRP_MN_QUERY_PNP_DEVICE_STATE`, requires `DeviceNodeStartPostWork` or `DeviceNodeStarted`, and returns the `PNP_DEVICE_STATE` flags.

Integration points:
- `devaction.c` uses these helpers to drive state transitions, enumeration, text/property setup, start/stop, and resource rebalance.
- Other files sometimes use the lower-level `IopInitiatePnpIrp`; this file provides the synchronized top-of-stack path where the state machine needs completion status and information.

Research notes:
- The implementation asserts APCs are not disabled before waiting, making callers responsible for pageable/passive context.
- Vista+ asynchronous behavior is mentioned in comments, but ReactOS currently performs these state-machine operations synchronously.
- Returned `Information` ownership remains with the caller; relation and resource lists are freed or stored by higher-level code.
