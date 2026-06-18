# File Research: sources/os/bsd/freebsd-src/sys/sys/bus.h

## Purpose
`bus.h` is the main FreeBSD newbus/device/resource interface header, covering user-visible device control structures, kernel driver APIs, resource management, interrupt setup, device classes, module registration, and bus-space convenience macros.

## Main Interfaces
- User ABI: `struct u_businfo`, `struct u_device`, device state enum, exported device flags, `struct devreq`, and `/dev/devctl2` ioctl constants for attach, detach, enable, disable, suspend, resume, driver selection, rescan, delete, freeze/thaw, reset, and path lookup.
- Kernel abstractions: `driver_t`, `devclass_t`, device methods, interrupt filter/handler types, interrupt type/trigger/polarity enums, bus ivar ranges, CPU set selectors, resource map structures, and resource lists.
- Generic bus helpers: child creation, resource allocation/activation/mapping/release, interrupt setup/teardown/suspend/resume, DMA/bus tag lookup, domain lookup, reset helpers, property lookup, and device path generation.
- Device/devclass APIs manage probing, attaching, detaching, softc, flags, state, sysctls, children, quiet/verbose settings, and driver classes.
- Boot pass constants order driver attachment from root and bus discovery through scheduler and default drivers.
- Module macros register drivers with buses, optionally in early passes.
- Generated bus-space wrappers operate on `struct resource *` for read/write/set/copy/barrier/peek/poke at 1/2/4/8-byte widths and stream variants.

## Implementation Notes
The header preserves compatibility with older bus resource APIs using `_Generic` and variadic macro dispatch. Device property types let firmware-backed buses normalize byte order or handles. Resource-map requests include size, offset, length, and memory attributes for controlled mapping.

## Dependencies and Constraints
The kernel section depends on `kobj`, eventhandlers, devctl, generated `device_if.h`/`bus_if.h`, and machine bus/DMA types. Many operations require holding the newbus topology lock; the header exposes lock/unlock/assert helpers.
