# File Research: sources/windows/winfsp/src/sys/device.c

Device object creation, initialization, lifetime, volume caches, context tables, and volume-info cache implementation.

Device creation/lifetime:
- `FspDeviceCreateSecure()` chooses extension size by device kind and calls `IoCreateDeviceSecure` or `IoCreateDevice`, initializes spinlock/refcount/kind.
- `FspDeviceCreate()` is the insecure unnamed wrapper.
- `FspDeviceInitialize()` dispatches kind-specific init and clears `DO_DEVICE_INITIALIZING` on success.
- `FspDeviceDelete()` dispatches kind-specific finalization then deletes the device.
- `FspDeviceDoIoDeleteDevice()` ensures `IoDeleteDevice` runs once.
- `FspDeviceReference()` / `FspDeviceDereference()` manage refcount under spinlock; dereference deletes at zero.
- DPC-level reference helpers are used by timer code and assert no deletion from DPC dereference.

Volume device init/fini:
- Initializes optional fsext provider.
- References virtual disk object and allocates swap VPB if mounted on virtual disk.
- Creates IO queue with timeout.
- Creates metadata caches for security, directory info, stream info, and EA.
- Initializes notify systems, statistics, delete/rename resources, context list, context-by-name AVL table, expiration timer/work item, and volume-info spinlock.
- Finalization stops timer first, then tears down statistics, notify, caches, IOQ, resources, virtual disk reference/VPB, and provider.

Expiration:
- `FspFsvolDeviceTimerRoutine()` runs at DPC, references the device, prevents duplicate expiration work item queuing, and queues passive-level work.
- `FspFsvolDeviceExpirationRoutine()` invalidates expired metadata caches, runs provider expiration, removes expired IOQ items, clears in-progress flag, and dereferences the device.

Context management:
- `FspFsvolDeviceCopyContextList()` snapshots active file-node contexts from a list.
- `FspFsvolDeviceCopyContextByNameList()` snapshots AVL table contexts.
- Enumerate/lookup/insert/delete helpers wrap the context-by-name AVL table.
- Compare uses `FspFileNameCompare` with case sensitivity derived from volume params.
- Allocation callback returns caller-provided element storage; free callback is no-op.

Volume information:
- `FspFsvolDeviceGetVolumeInfo()` copies cached info under spinlock.
- `FspFsvolDeviceTryGetVolumeInfo()` returns cached info only if expiration time is valid.
- `FspFsvolDeviceSetVolumeInfo()` updates info and sets expiration from volume params.
- `FspFsvolDeviceInvalidateVolumeInfo()` clears expiration.

Other device kinds:
- Fsvrt init/fini initializes mount mutex and frees mount-point buffer.
- Fsmup init/fini initializes prefix/class prefix tables and asserts emptiness on fini.
- `FspDeviceCopyList()` wraps `IoEnumerateDeviceObjectList`.
- `FspDeviceDeleteList()` dereferences enumerated device objects and frees the list.
- Defines global `FspDeviceGlobalMutex`.

Primary role:
- Centralizes WinFsp kernel device object lifecycle and per-volume shared infrastructure.
