# File Research: sources/os/linux/linux/mm/hugetlb_sysfs.c

## Purpose

`hugetlb_sysfs.c` builds the sysfs interface for HugeTLB hstates under `/sys/kernel/mm/hugepages` and, on NUMA systems, per-node HugeTLB directories under node devices. It exposes pool sizing, free/reserved/surplus counts, overcommit limits, optional mempolicy-based resizing, and demotion controls.

## Global Hstate Interface

During `hugetlb_sysfs_init()`, the file creates `mm_kobj/hugepages`, then one hstate kobject per HugeTLB page size using the hstate name such as `hugepages-2048kB`. Each hstate gets the common attribute group:

- `nr_hugepages`: read/write persistent pool size.
- `nr_overcommit_hugepages`: read/write surplus overcommit limit.
- `free_hugepages`: read-only free count.
- `resv_hugepages`: read-only global reservation count.
- `surplus_hugepages`: read-only surplus count.
- `nr_hugepages_mempolicy` under `CONFIG_NUMA`: read/write pool size honoring caller mempolicy.

Read helpers use `kobj_to_hstate()` to resolve whether a kobject is global or node-specific. Writes parse unsigned long values and call `__nr_hugepages_store_common()` with the resolved hstate and node id. Overcommit writes update `h->nr_overcommit_huge_pages` under `hugetlb_lock` and reject hstates whose gigantic pages cannot be managed at runtime.

## Demotion Interface

If an hstate has `h->demote_order`, `hugetlb_sysfs_add_hstate()` also creates a demotion attribute group:

- `demote`: write-only count of free huge pages to demote.
- `demote_size`: read/write target huge page size.

`demote_store()` parses the requested count, chooses either a single-node or all-memory-node mask, takes `h->resize_lock` and `hugetlb_lock`, checks free unreserved availability, and calls `demote_pool_huge_page()` until the request is satisfied or an error occurs. `demote_size_store()` parses a size, requires it to match an existing hstate with smaller order and at least `HUGETLB_PAGE_ORDER`, and updates `h->demote_order` under the resize lock.

## NUMA Node Interface

Under `CONFIG_NUMA`, the file maintains `node_hstates[MAX_NUMNODES]`, each with a `hugepages` kobject and per-hstate child kobjects attached to the node device. Per-node hstate directories expose a subset of attributes:

- `nr_hugepages`
- `free_hugepages`
- `surplus_hugepages`

`hugetlb_register_node()` creates these directories for a node after sysfs initialization, while `hugetlb_unregister_node()` removes demotion and per-node groups and drops kobject references. `hugetlb_register_all_nodes()` registers all online nodes during HugeTLB sysfs init. `kobj_to_node_hstate()` maps a node hstate kobject back to its global hstate and node id.

## Integration and Error Handling

The file relies on `hugetlb_internal.h` for the shared resize and demotion helpers. Sysfs setup is best-effort: failure to create one hstate logs an error, while failure to add demotion attributes removes the partially created hstate group. NUMA registration is guarded by `hugetlb_sysfs_initialized` so node hotplug callbacks before HugeTLB setup do not create incomplete directories.
