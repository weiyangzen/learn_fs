# File Research: sources/os/linux/linux/mm/hugetlb_vmemmap.c

Implements HugeTLB Vmemmap Optimization (HVO): deduplicating `struct page` backing memory for hugetlb folios by remapping most vmemmap PTEs to shared read-only tail metadata pages, then freeing redundant vmemmap pages.

Key flow:
- `vmemmap_remap_range()` walks kernel page tables for vmemmap ranges under `init_mm`, splitting PMD mappings when needed and optionally remapping PTEs.
- `vmemmap_remap_free()` replaces a hugetlb folio’s vmemmap mappings with a copied head page and a per-zone shared tail page, collecting old vmemmap pages for later free.
- `vmemmap_remap_alloc()` restores optimized vmemmap by allocating replacement pages and remapping them back.
- `hugetlb_vmemmap_optimize_folio(s)()` and `hugetlb_vmemmap_restore_folio(s)()` are the public HVO transitions used by hugetlb code.
- Boot-time pre-HVO support under `CONFIG_SPARSEMEM_VMEMMAP_PREINIT` can preinitialize section metadata for aligned gigantic bootmem hugetlb pages.

Important dependencies:
- Uses `init_mm.page_table_lock`, `walk_kernel_page_table_range()`, TLB flushing, `memmap_pages_add()`, `memmap_boot_pages_add()`, `init_compound_tail()`, and sparsemem helpers.
- Exposes runtime control via early param `hugetlb_free_vmemmap=` and sysctl `vm.hugetlb_optimize_vmemmap`.

Critical invariants:
- HVO requires `hugetlb_vmemmap_optimizable(h)` and skips already optimized folios.
- Head vmemmap page remains writable; tail entries are mapped read-only.
- Delayed TLB flushing is carefully coordinated when optimizing/restoring batches.
- Memory-hotplug self-hosted vmemmap pages are rejected with `-ENOTSUPP`.
