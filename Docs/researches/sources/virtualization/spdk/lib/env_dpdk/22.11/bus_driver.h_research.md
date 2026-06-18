# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/bus_driver.h

Vendored DPDK 22.11 internal bus-driver header. In 22.11, bus driver internals moved out of the public `rte_bus.h`, so this file carries the callback typedefs, full `struct rte_bus`, bus list type, scan policy/config definitions, and registration macros needed by SPDK compatibility code.

Compared with the 22.07 public header, this internal header adds `rte_bus_cleanup_t` and a `cleanup` method in `struct rte_bus`, includes newer internal annotation via `__rte_internal` on register/unregister APIs, and depends on the public `rte_bus.h`, `rte_dev.h`, EAL, and tailq headers.

It keeps the same core model: buses scan devices, probe drivers, find/plug/unplug devices, parse names/devargs, map/unmap DMA, expose IOMMU class, iterate devices, and handle hot-unplug/SIGBUS events.
