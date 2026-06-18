# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcopy_device.h

Provider-side registration interface for DMA copy devices. It defines private command state managed by dcopy, callback vectors implemented by DMA drivers, device info registration payloads, and notification/unregistration APIs.

Key elements:
- `dcopy_cmd_priv_s` is allocated during driver command allocation and attached to `dcopy_cmd_t.dp_private`; DMA drivers may only use `pr_device_cmd_private` directly.
- Private command state includes blocking-poll initialization, list node, wait flag, mutex/CV, backpointer to command, channel pointer, and device-private pointer.
- `dcopy_device_cb_t` version 0 contains callbacks for channel allocate/free, command allocate/free, command post/poll, and asynchronous unregister completion.
- Channel allocation callback receives device private state, dcopy channel handle, flags, requested size, query info output, and channel-private storage.
- `dcopy_device_info_t` registers devinfo node, static callback vector, DMA engine count, max transfer, capabilities, and device id.
- `dcopy_device_handle_t` is the opaque registered-device handle.
- `dcopy_device_register()` and `dcopy_device_unregister()` manage DMA device registration; unregister may return pending until channels drain.
- `dcopy_device_channel_notify()` reports channel events such as command completion to the dcopy framework.

Dependencies:
- Includes public `dcopy.h` and kernel device/list/synchronization types through related headers.
- Implemented by DMA engine drivers and consumed by the dcopy framework.

Research notes:
- The split private state prevents DMA drivers from corrupting framework polling/lifetime fields while still allowing driver-owned command metadata.
- Unregister is asynchronous when clients still hold channels; drivers must wait for `cb_unregister_complete()` before detach is safe.
