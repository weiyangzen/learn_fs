# File Research: sources/windows/winfsp/src/sys/fsext.c

## Role

Implements the WinFsp filesystem extension-provider registry and transaction helper. It allows external kernel providers to register custom FSCTL transaction handlers and lets the main driver lazily load providers based on registry configuration.

## Provider Registry

The provider registry is intentionally small and simple:

- Maximum providers: `FSP_FSEXT_PROVIDER_COUNTMAX` = 16.
- Storage: parallel arrays of control codes and provider pointers.
- Synchronization: `FsextSpinLock`.
- Lookup: linear scan by `DeviceTransactCode`.

`FspFsextProviderRegister` finds an empty slot, writes the provider’s device-extension offset to `FSP_FSVOL_DEVICE_EXTENSION.FsextData`, stores the provider control code and pointer, and returns `STATUS_TOO_LATE` if all slots are full.

## Lazy Loading

`FspFsextProvider` first checks the in-memory registry. If no provider is found and the caller supplied `PLoadResult`, it looks under `FSP_REGKEY\Fsext` for a registry value named as the 8-digit hex control code. The value must be `REG_SZ` naming a service. The function builds the service registry path under `CurrentControlSet\Services`, calls `ZwLoadDriver`, tolerates `STATUS_IMAGE_ALREADY_LOADED`, then checks the in-memory registry again. It returns `STATUS_OBJECT_NAME_NOT_FOUND` if the driver loaded but did not register the expected provider.

## Transactions

`FspFsextProviderTransact` builds a synchronous internal transaction IRP to WinFsp using `IoBuildDeviceIoControlRequest(FSP_FSCTL_TRANSACT_INTERNAL)`. Because that helper builds an IOCTL IRP without a file object, this function patches the next stack location to be `IRP_MJ_FILE_SYSTEM_CONTROL`, minor `IRP_MN_USER_FS_REQUEST`, and sets `FileObject`. It also marks the IRP as `IRP_SYNCHRONOUS_API` so `CancelSynchronousIo` can cancel it.

The function asserts that special kernel APCs are enabled, matching the documented `IoBuildDeviceIoControlRequest` caveat.

## Integration Points

This file is used by the private FSCTL dispatch path in `fsctl.c` for extension control codes. It includes public extension definitions from `<winfsp/fsext.h>` and relies on registry helpers plus normal Windows driver loading.

## Edge Cases And Risks

- Registration has no duplicate-control-code check; a later provider with a duplicate code could occupy another slot, but lookup returns the first match.
- The fixed 16-provider limit is deliberate because lookup is linear.
- Transaction IRPs are patched from device-control shape into filesystem-control shape, so correctness depends on stack-location fields being set consistently.
