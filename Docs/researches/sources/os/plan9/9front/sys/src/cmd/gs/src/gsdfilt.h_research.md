# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdfilt.h

This header defines the device filter abstraction.

A `gs_device_filter_t` provides three callbacks:
- `push`: create a filtered device targeting an existing device.
- `prepop`: prepare the top filtered device for removal.
- `postpop`: finish cleanup after the original target has been restored.

The comments describe the model: the graphics state owns a chain of devices where each filter forwards requests to its target, ending at the physical `setpagedevice` device. Shadow stack objects track the chain.

Public API:
- `gs_push_device_filter`
- `gs_pop_device_filter`
- `gs_clear_device_filters`

The header also declares the GC structure descriptor `st_gs_device_filter`.
