# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdfilt.c

This file implements graphics-state device filter stack management.

Core operations:
- `gs_push_device_filter` allocates a stack node, asks the filter to create/wrap a new device, links it above the current device, and installs it with `gs_setdevice_no_init`.
- `gs_pop_device_filter` calls filter `prepop`, restores the saved next device, frees stack references, calls `postpop`, and releases the popped top device.
- `gs_clear_device_filters` repeatedly pops until the stack is empty.

The stack node stores:
- `next`
- filter pointer `df`
- saved downstream device `next_device`

Reference counting is central. The code increments current-device references before wrapping, decrements the new wrapper after installing it into the graphics state, and carefully manages popped devices and stack nodes.

The implementation includes many device-related headers because filters operate by replacing the current `gx_device` while preserving graphics-state semantics.
