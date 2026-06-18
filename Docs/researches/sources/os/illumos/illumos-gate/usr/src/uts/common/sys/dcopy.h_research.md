# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcopy.h

Private DMA copy API for IP stack use. It defines the upper-layer client interface for discovering DMA copy engines, allocating channels and commands, posting physical-address copy commands, and polling or blocking for completion.

Key elements:
- Warns that the interface is private to the IP stack.
- Declares `uioa_dcopy_enable()` and `uioa_dcopy_disable()` to toggle dcopy KAPI integration in `uioa`.
- Defines common return statuses: failure, success, no resources, pending, and completed.
- `dcopy_query_t` reports the number of DMA channels in the system.
- `dcopy_handle_t` is an opaque channel handle.
- Allocation flags distinguish sleeping and non-sleeping allocation.
- `dcopy_alloc()` allocates a channel with in-order command completion; `dcopy_free()` releases it.
- `dcopy_query_channel_t` reports DCA support, device id/capabilities, channel size, and device-local channel number.
- Command version and command type currently define physical-address copy.
- Command flags support queuing without notify, no status, DCA target, completion interrupt, no-wait resource handling, source/destination snoop disabling, loop descriptors, and internal sync.
- `dcopy_cmd_copy_t` carries source physical address, destination physical address, and size.
- `dcopy_cmd_t` is a pointer to `struct dcopy_cmd_s`, which stores version, flags, command selector, command union, DCA id, and private command state.
- `DCOPY_ALLOC_LINK` allows command-allocation chaining for bulk free through the last command.
- Command lifecycle APIs allocate/free, post, and poll commands; blocking poll is only allowed in base context and requires interrupt generation.

Dependencies:
- Uses core kernel types from `sys/types.h`; provider-side details are in `dcopy_device.h`.
- Tied to DMA engines that understand physical copy commands and optional DCA/cache-snoop capabilities.

Research notes:
- Commands cannot be reused or freed until polling reports failure or completion.
- `DCOPY_CMD_NOSTAT` prevents later completion polling for that command, so callers must structure batches carefully.
- Channel allocation does not grant exclusive engine access; it guarantees ordering for commands posted through that channel.
