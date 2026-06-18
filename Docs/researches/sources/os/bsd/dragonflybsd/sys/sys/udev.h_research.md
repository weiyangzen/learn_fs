# File Research: sources/os/bsd/dragonflybsd/sys/sys/udev.h

## Summary
DragonFly udev event/ioctl ABI and kernel helper declarations.

## Main Responsibilities
- Declares kernel helpers to set/delete device property dictionary keys and emit attach/detach events.
- Defines `UDEVPROP` and `UDEVWAIT` ioctls.
- Defines event types, property update/remove keys, filter types, and default udevd listen socket path.
- Defines `struct udev_event` carrying an event type and property dictionary.

## Important Behavior
Kernel builds include queue/conf support and expose `cdev_t`-based helper APIs; userland builds include proplib for `prop_dictionary_t`.

## Risks
The socket path is hard-coded as `/tmp/udevd.socket`. The header’s userland-facing structures depend on proplib types, so consumers must preserve the expected include/visibility environment.
