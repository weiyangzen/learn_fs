# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpreport.c

Read status: complete file, 551 lines.

This file handles APIs used by drivers to report detected legacy/root-enumerated devices, resource detection/conflict checks, and custom target-device change notifications.

Key entry points:
- `IopGetInterfaceTypeString()` maps `INTERFACE_TYPE` values to registry-friendly strings used in generated compatible IDs.
- `IoReportDetectedDevice()` creates or accepts a PDO, allocates a device node, creates the Enum instance key, writes `Service`, `Legacy`, `DeviceReported`, compatible IDs, device text, and resource data, optionally assigns resources, inserts the node under the root, and queues enumeration.
- `IoReportResourceForDetection()` validates supplied resource lists and calls `IopDetectResourceConflict()`.
- `PpSetCustomTargetEvent()` sends a custom target-device notification through `PiNotifyTargetDeviceChange()` and optionally completes a caller event/status pair.
- `IoReportTargetDeviceChange()` validates a PDO and custom notification, rejects system remove events, sends the notification synchronously, and waits for completion.
- `IoReportTargetDeviceChangeAsynchronous()` copies the caller's custom notification into a nonpaged work item and queues delayed work.
- `IopReportTargetDeviceChangeAsyncWorker()` sends the queued custom notification and releases the referenced PDO.

Important dependencies:
- Root enumerator helpers: `PnpRootCreateDevice`, `PnpRootRegisterDevice`.
- Device-node creation and insertion: `PipAllocateDeviceNode`, `PiInsertDevNode`, `PiSetDevNodeState`.
- Registry setup: `IopCreateDeviceKeyPath`, `IopSetDeviceInstanceData`, `PiSetDevNodeText`.
- Resource assignment/conflict detection: `IopAssignDeviceResources`, `IopDetectResourceConflict`.
- Notification delivery: `PiNotifyTargetDeviceChange`.

Notable behavior and risks:
- Built-in drivers using `IoCreateDriver()` have `ServiceKeyName` shortened to the last path component before root-device IDs are generated.
- Newly reported devices get `DNF_MADEUP | DNF_ENUMERATED`, then are placed in `DeviceNodeStartPostWork` and re-enumerated.
- `ResourceAssigned == FALSE` causes immediate resource assignment; otherwise the supplied resources are recorded without assignment in this path.
- `PpSetCustomTargetEvent()` accepts asynchronous callback/context parameters but never invokes the completion callback, so asynchronous callers get `STATUS_PENDING` without callback completion from this file.
- The synchronous path sets the event before writing `SyncStatus = STATUS_SUCCESS`, which is a small ordering risk on multiprocessor systems.
