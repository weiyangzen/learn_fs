# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_dev.h

Defines the NV cache device-type interface and constructor registration macro.

Interface includes optional operations for:
- Init/deinit.
- Chunk open/close notification.
- Bdev compatibility.
- Chunk active check.
- Write path.
- Periodic processing.
- Open-chunk recovery.
- Backend-specific layout setup.
- Metadata layout operations.

The `FTL_NV_CACHE_DEVICE_TYPE_REGISTER()` macro registers static descriptors at module load via constructor.
