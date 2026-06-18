# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_dev.h

Vendored DPDK 22.11 public device API header. It forward-declares bus, devargs, device, and driver structs, adds accessor functions for driver name, device bus, bus info, devargs, driver, device name, and NUMA node, and keeps public device management APIs.

It defines device event types/callbacks, deprecated function-pointer guard macros, device policy enum, memory resource representation, device name length, probed-state query, hotplug add/remove, device probe/remove, comparison callback type, PMD export metadata macros, device iterator APIs, event callback APIs, event monitor start/stop, hotplug handling enable/disable, and experimental device DMA map/unmap.

The concrete driver/device struct definitions are intentionally moved to `dev_driver.h`, matching DPDK’s 22.11 public/internal header split.
