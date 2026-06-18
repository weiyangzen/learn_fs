# File Research: sources/os/linux/linux/mm/mmap.c

Linux core user virtual-address-space management. This file implements major mapping syscalls and helpers around `brk`, `mmap`, `munmap`, deprecated `remap_file_pages`, process mmap teardown, special kernel mappings, mmap sysctls, and fork-time VMA duplication.

Key responsibilities:
- Implements `brk`, `mmap_pgoff`, legacy `old_mmap`, `munmap`, deprecated `remap_file_pages`, and `vm_brk_flags()`.
- Provides `do_mmap()` and `ksys_mmap_pgoff()` validation and setup for anonymous, file-backed, hugetlb, shared/private, droppable, locked, populated, noreserve, and memfd-sealed mappings.
- Provides generic bottom-up/top-down unmapped-area search and wrappers around architecture/file `get_unmapped_area()` hooks.
- Exports VMA lookup helpers including `find_vma()`, `find_vma_intersection()`, `find_vma_prev()`, and `mm_get_unmapped_area()`.
- Handles stack expansion, stack guard gap parsing, and fault-time read-to-write mmap-lock upgrade for legacy stack growth.
- Releases all VMAs in `exit_mmap()` using MMU notifiers, cache/TLB teardown, page-table freeing, maple tree destruction, and accounting cleanup.
- Implements special mappings such as vDSO/VVAR-style page-array mappings with custom fault/name/close/mremap behavior.
- Initializes mmap-related sysctls and overcommit reserve defaults, and updates reserves on memory hotplug.
- Implements `dup_mmap()` for fork, including maple tree duplication, VMA duplication, file mapping interval insertion, userfaultfd duplication, anon-vma setup, hugetlb private state, KSM/khugepaged fork hooks, page-table copying, and failure cleanup.

Important behavior:
- `do_mmap()` assumes the current mm is write-locked and returns either an address or error value. It only reports whether population is needed; callers do `mm_populate()`.
- Protection flags are translated through `calc_vm_prot_bits()`, `calc_vm_flag_bits()`, default mm flags, and execute-only pkey handling.
- `MAP_FIXED_NOREPLACE` is forced through fixed-address selection but rejects existing VMA intersections with `-EEXIST`.
- File mappings check file size overflow, access mode, append/swapfile restrictions, `MAP_SHARED_VALIDATE`, noexec mounts, file mmap support, memfd seals, and hugetlb alignment.
- Anonymous `MAP_DROPPABLE` mappings are forced noreserve, wipe-on-fork, dontdump, nonlocked, nonstack, and non-hugetlb.
- `brk()` updates `mm->brk` carefully around shrinking because successful unmap can drop the mmap lock.
- Generic unmapped-area search honors stack guard placement, `mmap_min_addr`, architecture address-space limits, top-down fallback, hugepage alignment, shmem THP area hooks, and LSM `security_mmap_addr()`.
- `remap_file_pages()` emulates old nonlinear remapping via a fixed shared mmap after read-lock lookup, security checking outside mmap lock, and write-lock revalidation.
- `exit_mmap()` first notifies secondary MMUs, unmaps pages under read lock, then takes write lock to clear the maple tree, free page tables, close/free VMAs, and unaccount memory.
- `dup_mmap()` builds a duplicate maple tree first, then replaces each duplicated slot with fully initialized child VMAs; on failure it unmaps and tears down only the initialized prefix.

Dependencies:
- Core MM: VMA/maple iterators, `mmap_region()`, `do_vmi_munmap()`, `do_brk_flags()`, VMA merge/split/insert helpers, page-table copy/unmap/free helpers, rmap, anon_vma, mempolicy, KSM, khugepaged, hugetlb, THP, mlock, overcommit, pkeys, userfaultfd, MMU notifiers, and TLB gather.
- VFS/security: files, inodes, mapping interval trees, `get_file()`/`fput()`, file mmap hooks, memfd seals, LSM mmap/mprotect hooks, audit, mounts, and noexec path checks.
- Architecture hooks: mmap layout, tagged-address handling, cache/TLB flushing, execute-only pkeys, stack growth direction, and `arch_*_mmap()` hooks.

Notable risks:
- Many paths deliberately drop, downgrade, or reacquire mmap locks; callers must handle invalidated VMAs and userfaultfd completion lists correctly.
- Fixed mappings and brk/mremap interactions rely on downstream unmap helpers to enforce VMA sealing and split/merge invariants.
- Fork duplication has complex cleanup paths because maple tree state, file interval trees, anon_vmas, userfaultfd contexts, and page tables are initialized in stages.
- Accounting for `VM_ACCOUNT`, locked memory, data limits, map-count limits, and overcommit reserves must remain paired with VMA mutation and unmap behavior.
- Special mappings forbid splitting and may fault SIGBUS past their page arrays; users must preserve their lifetime assumptions.
