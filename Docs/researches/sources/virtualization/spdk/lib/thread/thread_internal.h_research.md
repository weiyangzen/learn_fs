# File Research: sources/virtualization/spdk/lib/thread/thread_internal.h

This private header defines the internal layout of `struct spdk_io_channel`.

An I/O channel records its owning `spdk_thread`, associated internal `io_device`, reference count, deferred-destroy reference count, RB-tree linkage, and the device-specific destroy callback. It includes fixed padding and documents that modules allocate additional context immediately after the structure for hardware- or module-specific channel data.

The `SPDK_STATIC_ASSERT` requires the structure size to match the public ABI constant `SPDK_IO_CHANNEL_STRUCT_SIZE`. That keeps the private layout compatible with public macros and the common pattern where `spdk_io_channel_get_ctx()` returns memory immediately after the header.
