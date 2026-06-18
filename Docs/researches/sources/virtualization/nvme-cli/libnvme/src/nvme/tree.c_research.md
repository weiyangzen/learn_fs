# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/tree.c

## Role

Implements libnvme's sysfs-backed topology tree and many public tree APIs. It discovers hosts, subsystems, controllers, namespaces, namespace paths, sysfs attributes, transport handles, stats, basic namespace I/O helpers, configuration loading/dumping, and object lifecycle.

## Key Content

### Topology Scanning

- `libnvme_scan_topology()` scans controllers first, then subsystems, then applies an optional filter.
- Filtering helpers can remove subsystems, controllers, and namespaces after the tree is fully populated.
- `libnvme_refresh_topology()` frees current hosts and rescans.
- `libnvme_scan_ctrl()` discovers a controller from `/sys/class/nvme/<name>`.
- `libnvme_scan_namespace()` scans a namespace from the block sysfs path.
- `libnvme_rescan_ctrl()` refreshes namespaces and paths for an existing controller.

### Host and Subsystem Management

- `libnvme_host_get_ids()` resolves host NQN and host ID from, in order:
  - command-line arguments
  - first JSON-configured host
  - `/etc/nvme/hostid` and `/etc/nvme/hostnqn`
  - UUID embedded in host NQN
  - generated host ID/NQN fallback
- `libnvme_get_host()` resolves or creates a host object.
- `libnvme_lookup_host()` and `libnvme_lookup_subsystem()` find or allocate objects.
- `libnvme_init_subsystem()` reads subsystem attributes such as model, serial, firmware, `subsystype`, and `iopolicy`.
- Subsystem scan logic validates NQN consistency and creates a detached subsystem under the default host if needed.

### Controller Management

- `libnvme_ctrl_alloc()` parses controller transport/address data from sysfs and reuses existing controller objects through fabrics-aware matching.
- `libnvme_reconfigure_ctrl()` refreshes controller attributes, including firmware, model, state, queue count, serial, controller type, controller ID, discovery-controller type, physical slot, and fabrics security attributes.
- `libnvme_init_ctrl()` initializes a newly created controller instance from a kernel instance number.
- `libnvme_create_ctrl()` creates an in-memory controller from requested controller parameters.
- `libnvme_lookup_ctrl()` searches an existing subsystem for a matching controller or creates one.
- `nvme_deconfigure_ctrl()`, `libnvme_unlink_ctrl()`, and `libnvme_free_ctrl()` manage controller cleanup.

### Namespace and Path Management

- `libnvme_ns_open()` allocates a namespace and namespace head, detects modern multipath sysfs support, initializes namespace data, and sets generic names.
- `libnvme_ns_init()` reads namespace sysfs attributes:
  - `nsid`
  - `size`
  - logical block size
  - `eui`
  - `nguid`
  - `uuid`
  - optionally `csi`, `nuse`, and `metadata_bytes`
- If modern namespace attributes are unavailable, `libnvme_ns_init()` falls back to Identify Namespace passthrough.
- `libnvme_ctrl_scan_namespace()` links controller namespaces.
- `libnvme_subsystem_scan_namespace()` links subsystem namespaces.
- `libnvme_subsystem_set_ns_path()` associates namespace heads with path objects using modern multipath sysfs links where available, otherwise falls back to name parsing.
- `libnvme_ctrl_scan_path()` creates path objects and reads ANA state, NUMA nodes, ANA group ID, and queue depth.
- `libnvme_subsystem_lookup_namespace()` finds a namespace by NSID.

### Stats

- Path and namespace stats are double-buffered.
- `libnvme_update_stat()` parses Linux block `stat` format into read/write/discard/flush groups plus inflight and tick counters.
- Public getters return either raw counters or deltas depending on `diffstat`.
- Stats cover:
  - inflight I/O
  - I/O ticks
  - read/write ticks
  - read/write I/O counts
  - read/write sectors
  - sample interval

### Transport Handles and I/O Helpers

- Controllers and namespaces lazily open transport handles:
  - `libnvme_ctrl_get_transport_handle()`
  - `libnvme_ns_get_transport_handle()`
- Release helpers close cached handles.
- Namespace helpers issue common commands:
  - Identify Namespace
  - Identify Namespace Descriptors
  - Verify
  - Write Uncorrectable
  - Write Zeroes
  - Write
  - Read
  - Compare
  - Flush
- `libnvme_bytes_to_lba()` validates alignment and translates byte offset/count to starting LBA and zero-based block count.

### Config and Context

- `libnvme_read_config()`, `libnvme_dump_config()`, and `libnvme_dump_tree()` bridge to JSON config/tree functions.
- Application scoping is stored in the global context and can filter subsystem lookup.
- Object-freeing functions recursively release controllers, namespaces, paths, subsystems, hosts, and transport handles.

## Dependencies

- Uses sysfs scanning helpers from elsewhere in libnvme.
- Uses CCAN lists for intrusive object graph links.
- Uses cleanup macros for scoped cleanup.
- Uses public passthrough initializer helpers such as `nvme_init_identify_ns()`, `nvme_init_read()`, and `nvme_init_flush()`.
- Depends on private sysfs path helpers from `sysfs.c` and fabrics helpers from `tree-fabrics.c`.

## Research Notes

This file is the primary implementation of libnvme's view of kernel NVMe topology. It handles kernel-version drift explicitly, including older kernels lacking some sysfs namespace attributes and newer kernels exposing multipath namespace-head paths. It also supports `create_only` mode, where namespace/path scanning is skipped.

Memory ownership is manual but consistently handled through cleanup labels and recursive free helpers. The most error-prone areas are sysfs parsing, controller reuse matching, namespace/path linking by parsed names, and fallback Identify Namespace calls during namespace initialization.

## Filesystem/Storage Relevance

This is directly relevant to block-storage discovery. It maps kernel NVMe sysfs objects into user-space objects used by tools to inspect, configure, and operate NVMe controllers and namespaces. Namespace I/O helpers expose block-level operations that filesystems and storage diagnostics rely on indirectly.
