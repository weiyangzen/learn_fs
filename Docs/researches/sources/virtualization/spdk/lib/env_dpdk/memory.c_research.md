# File Research: sources/virtualization/spdk/lib/env_dpdk/memory.c

Implements SPDK’s DPDK-backed memory registration, memory maps, NUMA lookup, virtual-to-physical translation, and VFIO/IOMMU DMA mapping.

The generic `spdk_mem_map` is a sparse 256 TB virtual-address map. It stores 2 MB translations in second-level 1 GB tables and can fall back to 4 KB third-level maps for unaligned edges or finer-grained regions. Registration state uses a dedicated map with `REG_MAP_REGISTERED` and `REG_MAP_NOTIFY_START` flags so exact registration regions can be walked and unregistered in the same chunks they were registered.

Public memory registration APIs:
- `spdk_mem_map_alloc/free()` create maps and replay current registrations to notify callbacks.
- `spdk_mem_register()` validates 4 KB alignment, rejects overlapping registered ranges, marks pages registered, and notifies maps.
- `spdk_mem_unregister()` requires unregistering whole registered regions, handles 4 KB submaps inside 2 MB regions, clears registration state, and sends unregister notifications in reverse map order.
- `spdk_mem_reserve()` allocates map space with default translations without marking memory registered.
- `spdk_mem_map_set_translation()`, `clear_translation()`, and `translate()` manage and query translations, coalescing contiguous translated ranges through an optional callback.

`mem_map_init()` creates the registration map, registers a DPDK memory hotplug callback outside legacy-memory mode, and walks existing DPDK memsegs to register them. The hotplug callback registers/free-unregisters DPDK memory and, for external DPDK initialization without guaranteed `--match-allocations`, marks segments as `DO_NOT_FREE`.

Vtophys translation first uses DPDK memsegs, then PCI BAR resources, then DPDK/pagemap IOVA translation for non-DPDK memory. It supports IOVA-as-VA with VFIO/IOMMU by mapping virtual addresses as IOVAs, and IOVA-as-PA by mapping physical addresses, rejecting unsupported 4 KB PA-mode pages. PCI BAR translations account for IOMMU VA mode where the virtual address is already the DMA address.

VFIO support discovers DPDK’s `/dev/vfio/vfio` container fd, tracks whether normal or noiommu VFIO is active, stores requested DMA mappings, defers mapping until the first SPDK-managed PCI device is added, reference-counts physical mappings, unmaps on final device removal, and provides BAR-specific map/unmap helpers.

`vtophys_init()` creates the physical-refcount map, optional NUMA map, and optional vtophys map with notify callbacks. `spdk_vtophys()` returns translated DMA/physical addresses plus page offset, `spdk_mem_get_numa_id()` returns mapped socket id or `SPDK_ENV_NUMA_ID_ANY`, and `spdk_mem_get_fd_and_offset()` exposes DPDK memseg fd/offset for shared-memory consumers. `mem_disable_huge_pages()` and `mem_disable_vtophys()` disable optional maps based on env options.
