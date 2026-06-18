# File Research: sources/os/bsd/freebsd-src/sys/kern/bus_if.m

## Summary
Defines the FreeBSD KObj `bus` interface: methods implemented by bus drivers that own child devices, manage bus-specific instance variables, allocate resources, configure interrupts, and coordinate child lifecycle.

## Main Responsibilities
- Specifies child enumeration, probing notifications, attach/detach notifications, and driver-added callbacks.
- Defines resource allocation, activation, mapping, unmapping, adjustment, translation, release, and resource-list/rman access.
- Defines interrupt setup, teardown, suspend/resume, binding, trigger/polarity configuration, remapping, and descriptive metadata.
- Defines child metadata callbacks for PnP info, location, device path, properties, DMA tags, bus tags, VM domain, CPU sets, and reset preparation/post/reset.

## Key Methods
Important methods include `print_child`, `probe_nomatch`, `read_ivar`, `write_ivar`, `child_deleted`, `child_detached`, `driver_added`, `add_child`, `rescan`, `alloc_resource`, `activate_resource`, `map_resource`, `unmap_resource`, `deactivate_resource`, `adjust_resource`, `translate_resource`, `release_resource`, `setup_intr`, `teardown_intr`, `set_resource`, `get_resource`, `delete_resource`, `get_resource_list`, `get_rman`, `child_present`, `child_pnpinfo`, `child_location`, `bind_intr`, `config_intr`, `describe_intr`, `hinted_child`, `get_dma_tag`, `get_bus_tag`, `hint_device_unit`, `new_pass`, `remap_intr`, `suspend_child`, `resume_child`, `get_domain`, `get_cpus`, `reset_prepare`, `reset_post`, `reset_child`, `get_property`, and `get_device_path`.

## Defaults
The file supplies default implementations for unsupported resource allocation, interrupt remapping fallback, child add panic, reset hooks, rman/resource-list lookup, and many methods through `bus_generic_*`.

## Integration
The `.m` file is consumed by FreeBSD's interface generator to create typed dispatch wrappers/macros for bus methods. It is part of the kernel device model rather than a concrete bus implementation.

## Risks
Method contracts are broad and many drivers depend on their exact semantics. Defaults can hide missing implementation for optional methods, while required methods such as resource activation or interrupt setup must be supplied correctly by real bus drivers.
