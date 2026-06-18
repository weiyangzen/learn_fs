# File Research: sources/virtualization/spdk/lib/rdma_utils/rdma_utils.c

This file provides shared RDMA utility services: memory registration maps, protection-domain management, SPDK memory-domain wrappers, NUMA lookup for CM IDs, CQ polling, and work-completion error injection.

Memory maps are represented by `spdk_rdma_utils_mem_map`. `spdk_rdma_utils_create_mem_map()` normalizes access flags for iWARP, reuses an existing map with the same PD and flags by incrementing `ref_count`, or allocates a new map and `spdk_mem_map`. The map notify callback either asks custom NVMe RDMA hooks for an rkey or registers memory with `ibv_reg_mr()` and stores the `ibv_mr *` as the translation. Unregister notifications deregister MRs when SPDK owns them and clear translations. `spdk_rdma_utils_free_mem_map()` decrements the reference count, removes the map when it reaches zero, frees the underlying `spdk_mem_map`, and uses `spdk_free()` only for hook-backed DMA allocations.

`spdk_rdma_utils_get_translation()` returns either a key or MR translation depending on whether custom hooks are used. It asserts the translated length covers the requested range and logs an error when no MR translation exists.

Protection-domain utilities maintain a global sorted snapshot of RDMA devices from `spdk_rdma_cm_get_devices()`. `rdma_sync_dev_list()` compares the new context list with the previous one, adds devices by allocating PDs, marks removed devices, and frees old device arrays only after the new list is retained. `spdk_rdma_utils_get_pd()` synchronizes the device list, finds the matching context, increments its refcount, and returns the shared PD. `spdk_rdma_utils_put_pd()` decrements the PD refcount, removes devices only after they are both removed and unreferenced, then resyncs the list. A destructor marks all devices removed, drops refs, removes them, and frees the context list.

Memory-domain utilities provide a refcounted SPDK `spdk_memory_domain` per ibv PD. `spdk_rdma_utils_get_memory_domain()` reuses an existing domain or creates a new RDMA memory domain with `spdk_memory_domain_create()` and an RDMA context containing the PD. `spdk_rdma_utils_put_memory_domain()` decrements, destroys the SPDK memory domain at zero references, removes it from the global list, and returns `-ENODEV` for unknown domains.

`spdk_rdma_cm_id_get_numa_id()` derives a NUMA ID from an RDMA CM ID by reading the local address, resolving the network interface name, and reading `/sys/class/net/<ifc>/device/numa_node`; failures return `SPDK_ENV_NUMA_ID_ANY`.

`spdk_rdma_utils_poll_cq()` wraps `ibv_poll_cq()` and can inject synthetic work-completion errors into successful completions. `spdk_rdma_utils_inject_wc_error()` validates numerator/denominator rate settings, stores the desired `ibv_wc_status`, uses a memory barrier, and enables injection. `spdk_rdma_utils_cancel_wc_error()` disables injection and resets the rate/status.

The main invariants are refcount correctness for maps, PDs, and memory domains; avoiding duplicate MR registration for shared maps; keeping RDMA device context arrays alive while PDs are allocated; and only injecting errors into otherwise successful completions.
