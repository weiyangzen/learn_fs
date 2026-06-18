# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_udev.c

Implements DragonFlyBSD’s kernel udev interface layered over devfs character devices and proplib dictionaries.

Key data structures:
- `struct udev_event_kernel`: queued event plus TAILQ link.
- `struct udev_softc`: per-open clone state, marker for per-reader event position, unit, device pointer, opened/initiated state.
- Global `udevq` for open instances and `udev_evq` for event stream.
- Global locks: `udev_lk` for event/open state and `udev_dict_lk` for per-device dictionary access.

Dictionary handling:
- `udev_get_dict()` retains a device’s `si_dict` under a global dict lock.
- `udev_put_dict()` releases retained dicts and unlocks.
- Internal helpers set string, signed integer, unsigned integer, and delete keys.
- `udev_init_dict()` creates a per-device dictionary with name, devnum, kernel pointer, devtype, uid, gid, mode, major, minor, and driver.
- `udev_destroy_dict()` releases and clears a device dictionary.

Event handling:
- `udev_init_dict_event()` builds an event dictionary identifying device name, devnum, devtype, kernel pointer, and changed key.
- `udev_dict_set_cstr()`, `udev_dict_set_int()`, `udev_dict_set_uint()`, and `udev_dict_delete_key()` update device properties and queue key update/remove events.
- `udev_event_attach()` queues attach events, handling aliases by copying the base dictionary and changing name/alias state.
- `udev_event_detach()` queues detach events and destroys the device dictionary.
- `udev_event_insert()` queues events only after at least one client has initiated collection; otherwise it bumps sequence state when clients are open.
- `udev_clean_events_locked()` drops old events that all markers have passed.
- `udev_event_externalize()` wraps event type and event dictionary into an XML proplib payload.

Device interface:
- Autoclone `/dev/udev` creates per-open devices under `udevs/<unit>`.
- `udev_dev_open()` allows one open per clone and increments open count.
- `udev_dev_close()` destroys the clone, removes reader marker, cleans old events, returns clone unit, and frees softc.
- `udev_dev_read()` initiates collection on first read, blocks until an event is available unless nonblocking, externalizes one XML event, and advances the reader marker.
- `udev_dev_kqfilter()` supports `EVFILT_READ`; readiness is true if the reader marker has a later real event.
- `udev_dev_ioctl()` supports `UDEVPROP` command dictionaries and `UDEVWAIT` sequence waits.
- `udev_getdevs_ioctl()` enables event collection before scanning devfs, then returns an array of current device dictionaries using `devfs_scan_callback()`.

Filesystem relevance:
- Directly devfs-facing. This file exposes character device creation/removal/property changes to userland consumers and scans devfs for current devices. It depends on vnode/device interfaces and is important for device-node visibility in the filesystem namespace.
