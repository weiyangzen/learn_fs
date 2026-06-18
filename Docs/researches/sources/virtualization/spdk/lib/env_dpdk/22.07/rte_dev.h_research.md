# File Research: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_dev.h

Vendored DPDK 22.07 device/driver public header. It exposes generic driver and device layouts, device events, hotplug/probe/remove APIs, device iteration, PMD metadata export macros, and device-level DMA map/unmap prototypes.

`struct rte_driver` contains the driver list link, name, and alias. `struct rte_device` contains the device list link, name, assigned driver, bus pointer, NUMA node, and latest devargs. `struct rte_mem_resource` stores physical address, length, and mapped virtual address.

The header also defines event callback registration/unregistration/processing, event monitor start/stop, hotplug handling enable/disable, device iterator initialization/next APIs, `RTE_DEV_FOREACH`, PMD export macros for names, PCI tables, parameter strings, and kernel-module dependencies. DMA map/unmap are marked experimental and require memory pre-registration through DPDK external memory APIs.
