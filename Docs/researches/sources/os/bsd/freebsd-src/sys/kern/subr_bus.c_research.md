# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_bus.c

## Purpose
Implements FreeBSD's core kernel newbus framework: devclasses, devices, driver registration, probing/attachment, generic bus methods, resource-list helpers, root bus setup, device-tree sysctls, `/dev/devctl2` control operations, device path caching, device properties, and obsolete-feature diagnostics.

## Main Elements
- Core data structures:
  - `struct driverlink`: driver registration entry, bus pass, and deferred-probe flag.
  - `struct devclass`: driver list, parent class, unit-indexed device table, and devclass sysctl tree.
  - `struct _device`: kobj-backed device node with parent/children, driver/devclass/unit, state, flags, ivars, softc, properties, and sysctl state.
  - `struct device_prop_elm`: named per-device property with optional destructor.
- Topology and pass control:
  - `bus_topo_lock()`, `bus_topo_unlock()`, `bus_topo_assert()` currently use Giant.
  - `bus_get_pass()` and `bus_set_pass()` advance boot-time driver pass levels and trigger `BUS_NEW_PASS(root_bus)`.
  - `driver_register_pass()` tracks distinct bus pass levels.
- Devclass management:
  - `devclass_create()`, `devclass_find()`, parent-class inheritance, driver add/delete/quiesce, device table allocation, unit reservation, device and driver enumeration.
  - `devclass_driver_added()` recursively notifies matching buses when a driver appears.
  - `devclass_driver_deleted()` detaches matching devices when a driver is removed.
- Device lifecycle:
  - `device_add_child[_ordered]()`, `device_delete_child()`, `device_delete_children()`, and `device_find_child()`.
  - `device_probe_child()`, `device_probe()`, `device_probe_and_attach()`, `device_attach()`, `device_detach()`, `device_quiesce()`, `device_shutdown()`.
  - Driver selection probes candidate drivers in devclass and parent-devclass lists, honors bus pass levels and wildcard/fixed devclasses, and uses probe return priority.
  - Failed attach can either reset probe state for future retries or leave the device disabled when `hw.bus.disable_failed_devices` is set.
- Device attributes:
  - Getters for parent, children, driver, devclass, name/unit, description, flags, softc, ivars, state, quiet/enabled/alive/attached/suspended status.
  - Setters for description, flags, softc ownership, ivars, devclass, fixed devclass, driver, and unit.
  - Busy recursion via `device_busy()` / `device_unbusy()`.
- Resource helpers:
  - `resource_init_map_request_impl()` and `resource_validate_map_request()` normalize and bounds-check resource map requests.
  - `resource_list_*()` manages child resource entries, reserved resources, active-resource release, unreserve, printing, and purge.
  - `bus_generic_*()` provides generic child attach/detach/suspend/resume/reset, ivar, property, interrupt, resource, CPU set, DMA tag, bus tag, domain, path, and rescan behavior.
  - `bus_generic_rl_*()` implements resource-list-backed bus resource operations.
  - `bus_generic_rman_*()` implements rman-backed allocation, adjustment, release, activation, mapping, IRQ activation, and deactivation.
  - Public `bus_*()` wrappers delegate to parent bus methods for resources, interrupts, CPU sets, DMA tags, bus tags, domains, child pnp/location info, and presence.
- Root bus and module integration:
  - `root_bus_module_handler()` initializes global device list, creates `root0`, installs root driver, and initializes `devctl2`.
  - `root_bus_configure()` advances to `BUS_PASS_DEFAULT`.
  - `driver_module_handler()` handles driver module load, unload, and quiesce.
  - `bus_enumerate_hinted_children()` walks loader hints for bus-specific and generic child declarations.
- User/kernel introspection and control:
  - `hw.bus.info` and `hw.bus.devices` sysctls expose generation and flat device records.
  - `bus_data_generation_check()` / `bus_data_generation_update()` track device-tree changes.
  - `device_lookup_by_name()` and `find_device()` support direct lookup and `dev_lookup` event handlers.
  - `/dev/devctl2` ioctl handler supports attach, detach, enable, disable, suspend, resume, set/clear driver, rescan, delete, freeze/thaw, reset, and get path.
  - Freeze/thaw defers probe and nomatch actions until `device_do_deferred_actions()`.
- Device path and properties:
  - `device_get_path()` and `bus_generic_get_device_path()` construct locator paths, including FreeBSD-style `/nameunit` paths.
  - `dev_wired_cache_*()` caches locator/path strings for matching wired devices against `at` hints.
  - `device_set_prop()`, `device_get_prop()`, `device_clear_prop()`, `device_clear_prop_alldev()` manage named properties with destructors.
- Diagnostics:
  - BUS_DEBUG print functions dump devices, drivers, devclasses, and trees.
  - `_gone_in()` and `_gone_in_dev()` print or panic for deprecated/obsolete APIs depending on `debug.obsolete_panic`.
  - DDB commands show a specific device or all devices.

## Dependencies And Integration
This file is central to kernel driver infrastructure. It depends on kobj, module loading, sysctl, rman, resource hints, eventhandlers, taskqueue, VNET checks, random harvesting, domainset allocation, IOMMU property reporting, optional INTRNG IRQ hooks, and DDB. It provides the implementation behind many `<sys/bus.h>` APIs used by bus and device drivers.

## Risk Notes
This file is concurrency- and state-sensitive. Many operations require the bus topology lock, but the lock is currently Giant, so incorrect future locking changes could expose races. Probe/attach/detach state transitions must keep devclass tables, sysctls, softc ownership, driver kobj state, resource ownership, and user-visible generation counts consistent. `/dev/devctl2` is privileged and mutates live device topology; incorrect validation can detach, delete, or rebind active devices. Resource-list reserved/allocation flags are subtle and can leak or double-release resources if bus drivers misuse them.
