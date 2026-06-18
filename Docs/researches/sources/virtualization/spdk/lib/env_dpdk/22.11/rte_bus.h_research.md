# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_bus.h

Vendored DPDK 22.11 public bus API header. It forward-declares `struct rte_bus` and `struct rte_device` instead of exposing bus internals.

The public API provides bus-name retrieval, global bus scan/probe/dump, bus comparison type, bus find-by-callback/name/device, and common IOMMU class retrieval. Driver-facing struct definitions and registration helpers are intentionally split into `bus_driver.h`.
