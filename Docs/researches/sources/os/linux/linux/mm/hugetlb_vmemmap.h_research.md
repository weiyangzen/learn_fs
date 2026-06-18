# File Research: sources/os/linux/linux/mm/hugetlb_vmemmap.h

Header for HugeTLB Vmemmap Optimization.

Defines:
- `HUGETLB_VMEMMAP_RESERVE_SIZE` as one page.
- `HUGETLB_VMEMMAP_RESERVE_PAGES` as the number of `struct page` entries covered by that reserved page.
- Public HVO functions for optimize, restore, batch optimize/restore, and bootmem initialization when enabled.
- Inline disabled stubs when `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP` is off.

Key helpers:
- `hugetlb_vmemmap_size(h)` returns the byte size of vmemmap metadata for a hugetlb page.
- `hugetlb_vmemmap_optimizable_size(h)` returns reclaimable vmemmap bytes after reserving one metadata page; it requires `sizeof(struct page)` to be a power of two.
- `hugetlb_vmemmap_optimizable(h)` is the boolean predicate used by implementation and callers.

Design note:
The disabled stubs preserve hugetlb call sites without forcing feature ifdefs. The batch restore stub moves all folios to `non_hvo_folios` and returns zero, matching “nothing needed” semantics.
