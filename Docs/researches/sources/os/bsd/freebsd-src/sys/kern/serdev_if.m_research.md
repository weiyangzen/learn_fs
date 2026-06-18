# File Research: sources/os/bsd/freebsd-src/sys/kern/serdev_if.m

## Summary
Defines the FreeBSD kernel `serdev` bus interface for serial-controller umbrella drivers and their per-channel child devices.

## Main Responsibilities
- Describes an interface inherited from `device`.
- Lets an umbrella serial controller query child drivers for interrupt handlers.
- Lets an umbrella driver query pending interrupt status from a child UART/channel.
- Lets an umbrella driver ask whether a child channel is a system device that should not be reset or reconfigured.

## Key Methods
- `ihand(device_t dev, int ipend)`: returns a `serdev_intr_t *` interrupt handler for a pending interrupt source.
- `ipend(device_t dev)`: returns pending interrupt status, defaulting to `-1`.
- `sysdev(device_t dev)`: returns non-zero when the channel/mode is reserved for system use, defaulting to `0`.

## Important Behavior
The interface is aimed at multi-channel serial hardware where the parent manages shared hardware state and the children own individual channels. Default methods are intentionally conservative: no handler, unknown/no pending interrupt, and not a system device.

## Dependencies
Uses FreeBSD bus interface generation syntax and includes `sys/bus.h` and `sys/serial.h`.

## Risks
The generated interface assumes parent and child drivers agree on `ipend` values and handler semantics. A child that fails to report system-device status can let a parent reset or reconfigure a console/debug channel.
