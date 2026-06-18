# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_impldefs.h

This is the central private implementation definition header for illumos DDI device tree internals. It includes the core DDI property, devops, autoconf, mutex, page, DACF, fault-management, DMA, interrupt, hotplug, ISA, id-space, modhash, and bitset headers, which reflects its role as the connective tissue for devinfo-node state.

The dominant structure is `struct dev_info`, the in-kernel representation of a device tree node. It records tree relationships (`devi_parent`, child, sibling), binding/name/address data, nodeid/instance, driver ops, parent-private data, minor nodes, per-driver instance links, inherited bus operation provider pointers, power-management state, callback lists, fault-management handle, interrupt state, contracts, hotplug handles, property dynamic caches, bus-private data, and nexus-specific data. Code touching this file is usually operating below public DDI and must preserve assumptions made by autoconfiguration, devfs, hotplug, PM, FMA, and interrupt subsystems.

The file defines device state and transition flag families for online/offline/down/degraded/removed device state, bus quiesced/down state, and reconfiguration transitions such as attaching, detaching, onlining, offlining, DACF invocation, devfs event add/remove, and reset-needed. The `DEVI_*` macros both test and mutate those bitfields and are used throughout device configuration logic.

It also defines ancillary structures: `ddi_cb` callback list entries, `devi_port`, `devi_bus_priv`, `regspec`, `regspec64`, `rangespec`, attach/detach specs, `ddi_minor`, `ddi_minor_data`, `ddi_parent_private_data`, soft-state tables (`i_ddi_soft_state`, string-keyed soft state, string-id records), DMA implementation handles, callback queues, dynamic-property caches, encoded device-id implementation data, and saved PCI config/capability descriptors.

Architecture-specific DMA internals are present. SPARC and non-SPARC forms of `ddi_dma_impl_t` differ, and public-looking DMA handles ultimately depend on these private layouts. The flag families `DMP_*`, `_DMCM*`, DMA physical mapping callbacks, and shadow/lock/cache/bypass/no-sync flags are private implementation controls.

The device-id section defines the raw encoded `impl_devid` layout, magic/revision constants, length/type conversion macros, ASCII/binary device-id type conversion helpers, SCSI VPD type checks, and the `devid` property name. These support compatibility with libdevinfo’s device-id representation even though the implementation is property-based.

Research notes:
- This header is private ABI for the illumos kernel, not a stable driver-facing surface.
- `struct dev_info` field order and bit meanings are high-risk compatibility points for kernel modules.
- Device-state macros have side effects and often imply devfs event/report state changes.
- Includes many cross-subsystem dependencies, so small changes can affect autoconf, devfs, PM, hotplug, FMA, interrupts, and DMA.
