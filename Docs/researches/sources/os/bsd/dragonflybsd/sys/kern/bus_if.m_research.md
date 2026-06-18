# File Research: sources/os/bsd/dragonflybsd/sys/kern/bus_if.m

## Summary
Defines the DragonFly BSD `bus` kernel object interface consumed by the device method generator. It specifies parent-bus methods for child enumeration, resource management, interrupt management, and child metadata.

## Main Responsibilities
- Provides `bus` interface method declarations.
- Supplies defaults for generic child printing, driver-added handling, resource-list lookup, child-present checks, interrupt config, interrupt enable/disable, DMA tag retrieval, and failed resource allocation.
- Documents expected bus/child contracts for ivars, resources, interrupts, and PnP/location strings.

## Key Methods
- Child lifecycle and metadata: `print_child`, `probe_nomatch`, `read_ivar`, `write_ivar`, `child_detached`, `driver_added`, `add_child`.
- Resource handling: `alloc_resource`, `activate_resource`, `deactivate_resource`, `release_resource`, `set_resource`, `get_resource`, `delete_resource`, `get_resource_list`.
- Interrupt handling: `setup_intr`, `teardown_intr`, `enable_intr`, `disable_intr`, `config_intr`.
- Bus properties: `child_present`, `child_pnpinfo_str`, `child_location_str`, `get_dma_tag`.

## Important Behavior
`alloc_resource` defaults to `null_alloc_resource`, so buses that do not implement it fail allocation cleanly. The interrupt-disable contract explicitly says disabling prevents future handler calls but does not interlock with a currently running handler.

## Risks
This file defines generated ABI-style driver hooks. Signature drift or default behavior changes affect many bus and device drivers. Resource `rid` handling is bus-specific, so callers must not assume returned IDs equal requested IDs.
