# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/tree.h

## Purpose
Public libnvme topology/tree API header. It defines opaque handles for hosts, subsystems, controllers, namespaces, namespace heads, paths, and stats, plus traversal macros and public operations over the scanned NVMe object graph.

## Main Interfaces
- Opaque types: `libnvme_host_t`, `libnvme_subsystem_t`, `libnvme_ctrl_t`, `libnvme_ns_t`, `libnvme_path_t`, `libnvme_ns_head_t`.
- Global context helpers: application string setters/getters, namespace scan skipping, cached FD release.
- Host identity APIs: `libnvme_get_host()`, `libnvme_host_get_ids()`, PDC flag setters/getters.
- Iterators and macros for host, subsystem, controller, namespace, and path traversal, including safe variants for deletion during iteration.
- Topology lifecycle: scan controller, scan namespace, scan topology, rescan controller, refresh topology, free/unlink controller/subsystem/host/namespace.
- Config APIs: read JSON config, dump JSON config, dump internal tree.
- Sysfs accessors for subsystem/controller/namespace/path attributes.

## Behavior and Design Notes
The header exposes libnvme’s internal topology as a hierarchical object tree rooted in `struct libnvme_global_ctx`, while preserving ABI opacity for concrete structs. It supports both physical controller/namespace relationships and multipath namespace/path relationships. Public getters include identity, model/serial/firmware, ANA/path attributes, transport handle access, controller state, and namespace/controller stats.

## Filesystem/Storage Relevance
This is the main API surface for discovering and representing NVMe block devices and NVMe-oF fabrics topology. It is relevant to block-storage enumeration, multipath path-state inspection, sysfs-driven device metadata, and user-space storage tooling integration.
