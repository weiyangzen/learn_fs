# File Research: sources/os/linux/linux/mm/hugetlb_sysctl.c

## Purpose

`hugetlb_sysctl.c` registers `/proc/sys/vm` sysctl controls for the default HugeTLB hstate. It bridges text sysctl reads/writes to the core pool resize and overcommit logic in `hugetlb.c`, while also exposing the hugetlb shared-memory group and optional gigantic-page migration knob.

## Controls

The sysctl table registers:

- `vm/nr_hugepages`: read or resize the default hstate persistent huge page pool.
- `vm/nr_hugepages_mempolicy` under `CONFIG_NUMA`: same resize path, but honoring the caller's memory policy where possible.
- `vm/hugetlb_shm_group`: group id allowed to create SysV hugepage shared memory without extra privilege.
- `vm/nr_overcommit_hugepages`: read or update the default hstate surplus overcommit limit.
- `vm/movable_gigantic_pages` under `CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION`: global integer controlling movable gigantic-page behavior.

## Implementation Details

`proc_hugetlb_doulongvec_minmax()` duplicates the `ctl_table` before changing `.data`, avoiding races with the generic `proc_doulongvec_minmax()` handler. `hugetlb_sysctl_handler_common()` reads the default hstate's `max_huge_pages` into a temporary value, lets the proc helper parse/update it, then on writes calls `__nr_hugepages_store_common()` with or without mempolicy enforcement.

`hugetlb_overcommit_handler()` similarly parses into a temporary value and commits `h->nr_overcommit_huge_pages` under `hugetlb_lock`. It rejects writes for gigantic hstates without runtime support. All HugeTLB handlers return `-EOPNOTSUPP` when the architecture does not support huge pages.

`hugetlb_sysctl_init()` registers the table under `vm` during HugeTLB initialization.
