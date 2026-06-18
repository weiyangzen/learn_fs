# File Research: sources/windows/winfsp/src/sys/devctl.c

Handles fast and regular `IRP_MJ_DEVICE_CONTROL` paths.

Fast I/O device control:
- `FspFastIoDeviceControl()` only attempts fast path for waitable `FSP_IOCTL_TRANSACT` on fsctl devices.
- Validates input/output sizes, copies user buffers into nonpaged system buffer under exception handling, sets top-level IRP to fast-I/O sentinel, calls `FspVolumeFastTransact()`, copies output back, and frees the buffer.

Control device:
- `FspFsctlDeviceControl()` forwards `FSP_IOCTL_TRANSACT`, batch, and internal transact requests to `FspVolumeTransact()` when a volume context exists.

Virtual disk device:
- `FspFsvrtDeviceControl()` first handles storage query, then mountdev IOCTLs, then returns `STATUS_UNRECOGNIZED_VOLUME` for unknown IOCTLs to avoid blocking WinFsp mount attempts by foreign file systems.
- `FspFsvrtDeviceControlStorageQuery()` implements `IOCTL_STORAGE_QUERY_PROPERTY` for `StorageAccessAlignmentProperty`, returning sector-size alignment data to satisfy clients such as SQL Server.

Volume device forwarding:
- `FspFsvolDeviceControl()` forwards only if the volume advertises `DeviceControl`.
- Rejects kernel-originated IOCTLs.
- Allows only custom device types and `METHOD_BUFFERED`.
- Validates file object and max buffer sizes.
- Creates a user-mode `DeviceControl` request, shared-acquires the file node, copies input buffer, records output length, sets ownership, and posts.
- `FspFsvolDeviceControlComplete()` validates response buffer bounds, copies output to the system buffer, truncating with `STATUS_BUFFER_OVERFLOW` if needed.
- Finalizer releases file-node ownership.

Primary role:
- Supports WinFsp’s control protocol, selected virtual-storage compatibility IOCTLs, and safe user-mode forwarding of custom buffered file IOCTLs.
