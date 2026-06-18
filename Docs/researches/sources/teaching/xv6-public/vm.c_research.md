# File Research: sources/teaching/xv6-public/vm.c

Implements x86 virtual memory setup and per-process address spaces.

Key behavior:
- `seginit` initializes per-CPU kernel/user code/data segment descriptors.
- `walkpgdir` locates or allocates page-table entries.
- `mappages` maps virtual ranges to physical ranges with permissions.
- `setupkvm` creates a page directory with shared kernel mappings from `kmap`.
- `kvmalloc` creates the scheduler/kernel page table and switches to it.
- `switchkvm` and `switchuvm` load CR3 and configure TSS/kernel stack for the active process.
- `inituvm`, `loaduvm`, `allocuvm`, and `deallocuvm` build and resize user memory.
- `freevm` frees user pages and page-table pages.
- `clearpteu` removes user access from the stack guard page.
- `copyuvm` clones user memory for `fork`.
- `uva2ka` and `copyout` safely copy kernel data into user virtual addresses.

Important interactions:
- Kernel mappings are present in every process page table but protected by missing `PTE_U`.
- The process memory model is contiguous from 0 up to `sz`.
