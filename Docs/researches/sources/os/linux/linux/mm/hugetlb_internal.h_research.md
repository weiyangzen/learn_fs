# File Research: sources/os/linux/linux/mm/hugetlb_internal.h

## Purpose

`hugetlb_internal.h` collects internal HugeTLB helpers and declarations shared by the core, sysfs, sysctl, and CMA-adjacent implementation files. It is not a public HugeTLB API; it exists to keep cross-file internals consistent.

## Helpers

The key inline predicate is `hstate_is_gigantic_no_runtime()`, which detects hstates whose order is gigantic while runtime gigantic-page allocation/freeing is unsupported. Sysfs, sysctl, allocation, free, and resize paths use it to reject or skip operations that cannot work on such hstates.

The header also provides node-rotation helpers for pool balancing:

- `next_node_allowed()` advances within a nodemask and asserts a valid node.
- `get_valid_node_allowed()` repairs a saved next-node value that is outside the current allowed mask.
- `hstate_next_node_to_alloc()` returns and advances an external next-allocation node cursor.
- `hstate_next_node_to_free()` returns and advances an hstate's next-free node cursor.
- `for_each_node_mask_to_alloc` and `for_each_node_mask_to_free` wrap these helpers for bounded iteration over allowed nodes.

These helpers allow `hugetlb.c` to spread persistent huge page allocation/freeing across changing cpuset or mempolicy node masks without trusting stale cursor values.

## Cross-File Declarations

The header declares core pool manipulation and sysfs/sysctl entry points used across files:

- `remove_hugetlb_folio()`, `add_hugetlb_folio()`, `init_new_hugetlb_folio()`, and `prep_and_add_allocated_folios()`.
- `demote_pool_huge_page()` for sysfs demotion requests.
- `__nr_hugepages_store_common()` for sysfs and sysctl pool resizing.
- `hugetlb_sysfs_init()` and `hugetlb_sysctl_init()`.

When `CONFIG_SYSCTL` is disabled, `hugetlb_sysctl_init()` is an inline no-op so `hugetlb.c` can call it unconditionally.
