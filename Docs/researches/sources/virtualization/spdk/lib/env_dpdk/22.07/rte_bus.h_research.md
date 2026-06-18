# File Research: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_bus.h

Vendored DPDK 22.07 bus interface header used by SPDK compatibility code. It exposes the full bus object layout and bus driver callback typedefs in the public header.

It defines IOVA modes, scan/probe/find/plug/unplug/parse/devargs parsing callbacks, bus-level DMA map/unmap callbacks, hot-unplug and SIGBUS handlers, scan policies, bus configuration, and `rte_bus_get_iommu_class_t`.

`struct rte_bus` contains the registered-bus list link, name, scan/probe/find/plug/unplug/parse/devargs methods, DMA map/unmap methods, configuration, IOMMU class method, device iterator, and hot-unplug/SIGBUS handlers. The header also declares bus registration, unregistration, scan/probe/dump/find APIs and the `RTE_REGISTER_BUS` constructor macro.
