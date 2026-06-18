# File Research: sources/teaching/xv6-riscv/kernel/vm.c

Implements kernel and user virtual memory management.

Important behavior:
- `kvmmake()` builds the kernel direct-map page table for UART, virtio, PLIC, kernel text/data/RAM, trampoline, and kernel stacks.
- `kvminit()` and `kvminithart()` install kernel paging.
- `walk()` traverses/allocates Sv39 page tables.
- `walkaddr()` resolves user virtual pages.
- `mappages()` maps page-aligned ranges.
- `uvmcreate()`, `uvmalloc()`, `uvmdealloc()`, `uvmunmap()`, `uvmfree()`, and `freewalk()` manage user page tables and memory.
- `uvmcopy()` implements fork memory copying.
- `uvmclear()` makes the exec stack guard inaccessible to user mode.
- `copyout()`, `copyin()`, and `copyinstr()` move data across user/kernel boundaries.
- `vmfault()` lazily allocates pages for `sbrk`.
- `ismapped()` checks PTE validity.

Filesystem relevance: user path strings, I/O buffers, `stat` outputs, exec loading, and lazy user memory all depend on these copy and mapping routines.
