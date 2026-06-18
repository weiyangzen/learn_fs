# File Research: sources/os/bsd/netbsd-src/sys/sys/device_impl.h

Private autoconf-internal device layout and power-management helpers.

Key content:
- Explicit warning: do not use outside autoconf internals.
- `struct device_lock` with wait/lock counts, holder, mutex, condition variable.
- `DEVICE_SUSPENSORS_MAX`.
- Full `struct device` layout: handle, class, global list entry, config data, driver/attach pointers, unit/name, parent/depth, flags, private storage, locators, property dictionary, localcount, pending config state, attach/detach state, activity handlers, driver/bus/class PM callbacks, generation numbers, lock, suspensor arrays, garbage list.
- Private flags: active, power handlers registered, class/driver/bus suspended, attach in progress.
- PM helper declarations for driver/class registration, suspend/resume/shutdown, locks, and registration checks.

Important behavior:
- Complements `device.h`; the public API intentionally hides this layout.
- Flags must not overlap with `cfattach::ca_flags` values noted in `device.h`.
