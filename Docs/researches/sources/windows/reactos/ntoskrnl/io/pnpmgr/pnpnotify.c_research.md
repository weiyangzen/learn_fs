# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpnotify.c

Read status: complete file, 519 lines.

This file implements Plug and Play notification registration, delivery, and unregistration for device-interface changes, hardware-profile changes, and target-device changes.

Key entry points:
- `PiInitializeNotifications()` initializes guarded mutexes and list heads for notification categories.
- `PiNotifyDeviceInterfaceChange()` allocates a `DEVICE_INTERFACE_CHANGE_NOTIFICATION`, filters registrations by interface class GUID, and invokes matching callbacks.
- `PiNotifyHardwareProfileChange()` broadcasts a `HWPROFILE_CHANGE_NOTIFICATION` to all hardware-profile listeners.
- `PiNotifyTargetDeviceChange()` broadcasts target-device removal/custom notifications through the target device node's per-device notification list and fills the registered `FileObject` before each callback.
- `IoRegisterPlugPlayNotification()` allocates a `PNP_NOTIFY_ENTRY`, references the driver object, installs it on the relevant list, and optionally sends arrival notifications for existing interfaces.
- `IoUnregisterPlugPlayNotification()` marks an entry deleted and dereferences it under the category lock.
- `IoPnPDeliverServicePowerNotification()` is present but unimplemented.

Important dependencies:
- Global lists guarded by `PiNotifyDeviceInterfaceLock`, `PiNotifyHwProfileLock`, and `PiNotifyTargetDeviceLock`.
- Device-node target notification list: `deviceNode->TargetDeviceNotify`.
- Interface enumeration through `IoGetDeviceInterfaces()`.
- Target resolution through `IopGetRelatedTargetDevice()`.

Notable behavior and risks:
- Notification callbacks are invoked after temporarily releasing the guarded mutex. Entries are reference-counted first so unregister-during-callback remains survivable.
- `PiCallNotifyProc()` debug-checks that callbacks preserve IRQL and APC-disable state, but ignores callback return values.
- `PNP_NOTIFY_ENTRY.RefCount` is an 8-bit field, so extreme recursive/reentrant callback paths could overflow it.
- `PiNotifyTargetDeviceChange()` references the target `DeviceObject` before allocation, but the allocation-failure path returns without dereferencing it.
- Device-interface registrations with `PNPNOTIFY_DEVICE_INTERFACE_INCLUDE_EXISTING_INTERFACES` call the callback directly for existing links, outside the registered-entry refcount path.
