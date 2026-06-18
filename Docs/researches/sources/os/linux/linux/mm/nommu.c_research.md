# File Research: sources/os/linux/linux/mm/nommu.c

## Role

NOMMU implementation of core Linux virtual-memory interfaces for systems without page-table based virtual memory. It replaces many MMU-only facilities with direct kernel allocations, tracks executable/user mappings with `vm_region` records, implements `brk`, `mmap`, `munmap`, limited `mremap`, remote-memory access, and NOMMU inode mapping shrink behavior.

## Key Behavior

- Provides NOMMU versions of vmalloc APIs. Most allocation entry points (`vmalloc`, `vzalloc`, node variants, 32-bit variants, and `__vmalloc*`) are backed by `kmalloc`/`krealloc` with `__GFP_COMP` and no highmem. `vfree` is `kfree`; `vmalloc_to_page` and `vmalloc_to_pfn` use direct virtual-to-page translation.
- Explicitly rejects MMU-style remapping helpers that cannot work without page tables. `vmap`, `vunmap`, `vm_map_ram`, `free_vm_area`, `filemap_fault`, and `filemap_map_pages` hit `BUG()`, while `vm_insert_page(s)` and `vm_map_pages*` return `-EINVAL`.
- Maintains global shareable mapping state in `nommu_region_tree`, protected by `nommu_region_sem`. Each `vm_region` records real address range, top allocation bound, file reference, pgoff, flags, usage count, and icache-flush state.
- `mmap_init()` initializes `vm_committed_as`, creates the `vm_region` slab cache, registers `/proc/sys/vm/nr_trim_pages`, and initializes VMA state.
- `validate_mmap_request()` performs NOMMU-specific mmap admission. It rejects `MAP_FIXED`, invalid mapping types, zero/overflowing lengths, missing file mmap support, unsupported file types, disallowed shared writes, append conflicts, noexec executable mappings, and security address failures. It derives whether a mapping may be direct, copied, readable, writable, or executable.
- `determine_vm_flags()` converts requested protections, flags, and NOMMU capabilities into `vm_flags`, including `VM_MAYOVERLAY` for read-only private direct file mappings that may safely overlay file/device storage.
- `do_mmap()` is the central mapping constructor. It allocates a `vm_region` and VMA, handles sharing by scanning existing regions for compatible overlapping mappings on the same inode, calls file `get_unmapped_area()` for direct mappings, calls the file mmap operation for shared/direct mappings, or allocates and fills a private copy with `alloc_pages_exact()` and `kernel_read()`.
- Private copies are marked `VM_MAPPED_COPY`, counted in `mmap_pages_allocated`, and freed page-by-page by `free_page_series()` when the region usage count drops to zero.
- VMA registration updates `mm->mm_mt`, `map_count`, `total_vm`, file `i_mmap` interval trees, and icache state. File-backed VMAs hold file references both from the VMA and the shared region.
- `do_munmap()` is constrained by the absence of remappable page tables. File-backed mappings must be removed as whole VMA ranges; anonymous mappings may be split or shrunk at page-aligned edges. `split_vma()` duplicates the VMA/region for anonymous ranges, and `vmi_shrink_vma()` shrinks a single-usage private region and frees the removed pages.
- `exit_mmap()` tears down all VMAs, removes mapping interval-tree entries, drops files and regions, frees private copies, destroys the maple tree, and runs under the mmap write lock even though it is the final user.
- `mremap` only changes the size of an exact existing non-shared mapping in place, and only within the already allocated backing region. `MREMAP_FIXED` moves and shared mapping expansion are rejected.
- `remap_pfn_range()` only succeeds when the requested VMA address is already the direct physical address. `remap_vmalloc_range()` is allowed only for VMAs marked `VM_USERMAP` and retargets the VMA to the vmalloc allocation address.
- `access_remote_vm()` and `access_process_vm()` copy directly to or from another task's actual mapped addresses after finding a covering VMA and checking `VM_MAYREAD`/`VM_MAYWRITE`.
- Under `CONFIG_BPF_SYSCALL`, `copy_remote_vm_str()` copies a NUL-terminated string from a target task's address space with VMA bounds and permission checks.
- `nommu_shrink_inode_mappings()` prevents truncation from breaking shared page-cache mappings and shrinks tracked regions extending past the new file size.
- Initializes overcommit reserve sysctls for users and admins based on free pages. `dup_mmap()` only duplicates the executable-file reference because NOMMU has no forked address-space copy in the MMU sense.

## Dependencies

Depends on Linux VMA/maple-tree helpers, address-space interval trees, file `mmap` and `get_unmapped_area` callbacks, security mmap hooks, page allocator exact allocations, cache/TLB/icache helpers, uaccess copy helpers, sysctl registration, overcommit accounting, and NOMMU capability flags from kernel headers.

## Research Notes

The file is a compatibility layer, but it is not a thin stub. Its correctness depends on preserving the invariant that user-visible "virtual" mapping addresses are real allocated or device/file-supplied addresses. Sharing is tracked at the `vm_region` level rather than through page tables. The highest-risk areas are reference ownership between VMAs and regions, exact overlap rules for shareable mappings, and freeing only memory that was privately allocated rather than direct I/O or page-cache storage.
