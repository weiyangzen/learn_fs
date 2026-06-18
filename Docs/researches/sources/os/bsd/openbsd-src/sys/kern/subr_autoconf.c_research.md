# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_autoconf.c

## Role

Implements OpenBSD kernel autoconfiguration support: device matching, softc allocation, attach/detach, deferred configuration, mountroot-time callbacks, suspend/resume activation, global device lookup, and device reference management.

## Key Behavior

- `config_init()` initializes deferred queues and the global `alldevs` device list.
- `config_search()`, `config_scan()`, and `config_rootsearch()` walk generated `cfdata`/`cfroots` tables, filter unavailable or hibernate-skipped devices, and use match priority to choose the winning attachment candidate.
- `config_attach()` serializes against detach, allocates/uses softc storage, assigns unit numbers, updates `cfdriver` device arrays, marks `cfdata` state, calls `device_register()` and driver attach hooks, processes deferred children, and emits hotplug events.
- `config_make_softc()` creates and names device instances, expands `cd_devs`, and handles wildcard unit selection.
- `config_detach()` serializes against attach, deactivates devices, calls driver detach hooks, verifies child removal in diagnostic builds, frees unit/cfdata state, updates hotplug, and drops references.
- `config_defer()` and `config_process_deferred_children()` support child setup after a parent finishes attaching; `config_mountroot()` and `config_process_deferred_mountroot()` delay work until root is mounted.
- `config_suspend_all()` coordinates quiesce/suspend/powerdown/resume/wakeup ordering for `mpath` and `mainbus`.
- `config_activate_children()` walks direct children and rolls back already-suspended children on suspend failure.
- `device_lookup()`, `device_mainbus()`, `device_mpath()`, `device_ref()`, and `device_unref()` provide active-device lookup and lifetime management.

## Interfaces And Dependencies

Depends on generated kernel configuration tables, `struct cfdata`, `struct cfdriver`, `struct cfattach`, device classes, hotplug support, reboot flags, mutexes, atomic refcounts, `TAILQ`, and driver-supplied match/attach/detach/activate callbacks.

## Notes

The file is central to kernel device-tree lifetime. Correctness depends on keeping attach/detach serialization, `cf_fstate`, wildcard unit allocation, `cd_devs`, and device references consistent. Hibernate boot filters deliberately avoid some classes and drivers during unhibernate probing.
