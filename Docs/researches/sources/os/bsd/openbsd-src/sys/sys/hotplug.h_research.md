# File Research: sources/os/bsd/openbsd-src/sys/sys/hotplug.h

This header defines the public hotplug event structure and kernel notification hooks.

Key definitions:
- Event types: `HOTPLUG_DEVAT`, `HOTPLUG_DEVDT`.
- `struct hotplug_event` with event type, device class, and 16-byte device name.

Kernel APIs:
- `hotplug_device_attach`
- `hotplug_device_detach`

Risk notes:
- Device names are fixed-width and align with `struct device::dv_xname`.
- Depends on `enum devclass` from `device.h` being available to includers.
