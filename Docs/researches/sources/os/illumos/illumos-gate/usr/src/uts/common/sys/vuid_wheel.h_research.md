# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_wheel.h

`vuid_wheel.h` defines VUID mouse-wheel ioctl and data structures. It includes `sys/vuid_event.h` for the `VUIOC` ioctl base.

The header caps the supported wheel count at `VUID_WHEEL_MAX_COUNT` and defines ioctls to get wheel count, get wheel information, get wheel state, and set wheel state. `wheel_info` carries a version field, wheel ID, and format. Supported formats are unknown, horizontal, and vertical. `wheel_state` carries a version field, wheel ID, and state flags. The only defined state flag is `VUID_WHEEL_STATE_ENABLED`.

Wheel event values encode deltas in the low byte. `VUID_WHEEL_DELTAMASK` masks that byte, and `VUID_WHEEL_GETDELTA()` casts it to `signed char`, preserving negative wheel movement encoded in 8-bit two's-complement form.

This file is an ABI shim between VUID-aware input drivers and consumers that query wheel topology and enablement.
