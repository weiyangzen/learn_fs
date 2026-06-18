# File Research: sources/os/linux/linux-stable/fs/proc/page.c

Implements PFN-indexed binary proc files: `/proc/kpagecount`, `/proc/kpageflags`, and optionally `/proc/kpagecgroup`.

Key points:
- `kpage_read()` validates 64-bit alignment and walks PFNs up to `get_max_dump_pfn()`.
- Sparsemem rounds max PFN to section boundary to allow early section memmap inspection.
- `kpagecount` reports mapcount using precise or average folio mapcount helpers.
- `stable_page_flags()` snapshots page/folio state and maps internal flags to stable userspace KPF bits.
- Exports flags for mapped, anon, KSM, compound head/tail, hugetlb, THP, zero page, buddy, offline, pgtable, slab, idle, locked, dirty, LRU, referenced, active, reclaim, swapcache, mlocked, hwpoison, reserved, owner/private, and arch bits.
- `kpagecgroup` reports memory cgroup inode when `CONFIG_MEMCG`.
- All entries are permanent read-only proc files.

Dependencies/contracts:
- Stable binary ABI; consumers index by PFN and read `u64` records.
- Uses page snapshot APIs to reduce races while reporting live page state.
