# File Research: sources/os/linux/linux/fs/proc/page.c

## Scope

This file implements physical page inspection proc files: `/proc/kpagecount`, `/proc/kpageflags`, and optionally `/proc/kpagecgroup`.

## Public And Internal APIs Covered

- Shared read helper: `kpage_read()`.
- Count reader: `kpagecount_read()`.
- Flag exporter: `stable_page_flags()`.
- Flag reader: `kpageflags_read()`.
- Memcg reader: `kpagecgroup_read()` under `CONFIG_MEMCG`.
- Init: `proc_page_init()`.

## Control Flow And Behavior

- `get_max_dump_pfn()` extends sparsemem coverage to the containing section boundary so initialized early memmap pages can be inspected.
- `get_kpage_count()` snapshots the page and returns precise mapcount when configured, otherwise average folio mapcount.
- `kpage_read()` requires 64-bit entry alignment for offset and count, clamps reads to the dumpable PFN range, translates PFNs to online pages, emits operation-specific 64-bit values, and zeroes holes/offline pages.
- `stable_page_flags()` snapshots page and folio state, translates kernel page flags into stable userspace KPF bits, and adds pseudo flags for no-page, mmap, anon, KSM, compound head/tail, huge/THP/zero page, buddy, offline, page table, slab, idle, swapcache, mlocked, hwpoison, reserved, private, and arch flags.
- Init creates owner-read `kpagecount` and `kpageflags`, plus `kpagecgroup` when memcg is enabled.

## Dependencies

- Depends on page snapshots, folios, mapcount helpers from `internal.h`, memcg page cgroup inode lookup, KSM, huge/THP, hugetlb, page idle, memory hotplug, and kernel-page-flags ABI constants.

## Risks And Invariants

- Offsets and counts must be multiples of `sizeof(u64)`.
- Values are stable ABI-facing page diagnostics; flag bit meanings must stay compatible with userspace documentation.
- Page state is sampled and can race live memory changes; snapshot helpers reduce but do not eliminate temporal inconsistency.
