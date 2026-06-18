# File Research: sources/os/linux/linux/mm/init-mm.c

Defines the global kernel `init_mm` and a dummy VMA ops table.

Core content:
- `const struct vm_operations_struct vma_dummy_vm_ops;` provides an empty operations table used when a VMA’s real hooks must no longer be invoked after error/close paths.
- `struct mm_struct init_mm` initializes the kernel address-space descriptor with:
  - `swapper_pg_dir`
  - maple tree `mm_mt`
  - reference counts
  - mmap/page-table/arg locks
  - per-VMA lock state when configured
  - scheduler mm CID lock when configured
  - architecture `INIT_MM_CONTEXT()`

`setup_initial_init_mm()` records kernel text/data/brk boundaries in `init_mm`.

Importance:
This is foundational shared state. Many files in this group use `init_mm` directly for kernel page table operations, including HVO vmemmap remapping, generic ioremap, and KASAN shadow setup.
