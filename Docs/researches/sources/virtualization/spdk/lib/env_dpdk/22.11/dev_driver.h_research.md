# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/dev_driver.h

Vendored DPDK 22.11 internal device-driver header. It defines the concrete `struct rte_driver` and `struct rte_device` layouts that the 22.11 public `rte_dev.h` only forward-declares.

`struct rte_driver` retains the driver list link, name, and alias. `struct rte_device` retains the device list link, name, assigned driver, bus pointer, NUMA node, and latest devargs, and adds a `bus_info` string for bus-specific device description.
