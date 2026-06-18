# File Research: sources/os/linux/linux/mm/debug.c

Provides MM debugging dump helpers and flag-name tables. It centralizes human-readable output for pages, folios, VMAs, mm structs, and VMA merge state, and implements optional page-struct poisoning controlled by the `vm_debug` kernel parameter.

Key responsibilities:
- Exports migration reason names and trace print flag tables for page, GFP, and VMA flags.
- Maps encoded page types to short names such as slab, hugetlb, offline, guard, table, buddy, and unaccepted.
- Dumps folio/page state including refcount, mapcount, mapping, index, PFN, large-folio metadata, memcg data, KSM/anon/mapping type, flags, page type, raw `struct page` bytes, and head bytes for large folios.
- Exports `dump_page()` for page diagnostics and calls `dump_page_owner()`.
- Under `CONFIG_DEBUG_VM`, exports `dump_vma()`, `dump_mm()`, and `dump_vmg()`.
- Implements `vm_debug` parsing and `page_init_poison()`.
- Provides `vma_iter_dump_tree()` when maple-tree VMA debugging is enabled.

Important flows:
- `dump_page()` detects poisoned/uninitialized pages, otherwise snapshots the page before dumping so folio/page state is consistent enough for diagnostics.
- `dump_vma()` prints VMA bounds, mm, protection, anon_vma, vm_ops, file, private data, optional VMA refcount, and decoded flags.
- `dump_mm()` prints address-space layout, page-table pointer, refcounts, RSS/VM high-water marks, VM counters, code/data/stack/brk/arg/env bounds, flags, and optional subsystem fields.
- `dump_vmg()` prints the state of a `vma_merge_struct` and recursively dumps its mm and neighboring VMAs when present.
- `setup_vm_debug()` treats bare `vm_debug` as enabling all controllable debug features, supports `vm_debug=-` to disable page-init poisoning, and `vm_debug=p` to enable it.

Concurrency and diagnostic caveats:
- Pageblock/migration state can race while dumping; the code explicitly accepts this because output is diagnostic.
- Many helpers are compiled only with `CONFIG_DEBUG_VM`.
- Dump functions intentionally emit kernel log warnings/emergencies and are not normal control-path logic.
