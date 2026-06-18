# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/grow.c

## Purpose

`grow.c` implements user address-space growth and mapping syscalls: `brk`, stack growth, anonymous mmap, file mmap, munmap, mprotect, and mincore. It also handles large-page heap/stack policy, mmap address selection, ASLR, and NBMAND mapping conflicts.

Read completely: 1,077 lines.

## Main Responsibilities

- Implements `brk()` and heap extension/shrink in `brk_internal()`.
- Chooses large-page heap sizes through `brk_lpg()`.
- Implements stack growth through `grow()` and `grow_internal()`.
- Chooses large-page stack sizes through `grow_lpg()`.
- Chooses mmap addresses through `choose_addr()`.
- Implements anonymous mappings through `zmap()`.
- Implements shared/private file mappings through `smmap_common()`.
- Provides 64-bit and 32-bit syscall wrappers: `smmap64()`, `smmap32()`, and `smmaplf32()`.
- Implements `munmap()`, `mprotect()`, and `mincore()`.

## Heap Growth

`brk()` serializes heap changes with `as_rangelock()`. A zero argument returns the current break for `sbrk()` support. If automatic large pages are enabled, `brk_lpg()` chooses a page size through `map_pgsz()` and backs off to smaller pages on failure.

`brk_internal()` initializes `p_brkbase` on first use, enforces `RLIMIT_DATA`, rounds requested mappings to the selected page size, maps zero-fill-on-demand memory through `as_map()` and `segvn_create`, or unmaps to shrink. It maintains `p_brksize` as the process heap size.

## Stack Growth

`grow()` serializes stack changes with `as_rangelock()`, calls the large-page or base implementation, and pre-faults newly granted stack pages with `as_fault()`.

`grow_internal()` assumes downward-growing stacks, enforces `RLIMIT_STACK`, avoids shrinking, sets executable-stack permissions from `p_stkprot`, and maps new stack memory through `segvn_create`. It can shrink the stack guard segment if the stack limit was expanded, but refuses to shrink the guard below `stack_guard_min_sz`.

## Address Selection And ASLR

`choose_addr()` accepts fixed mappings by unmapping the requested range. For non-fixed mappings it first tries the supplied hint unless randomization or alignment policy overrides it, then calls `map_addr()`.

`aslr_respect_mmap_hint` controls whether non-null unaligned hints suppress randomization. `smmap_common()` adds `_MAP_RANDOMIZE` when ASLR is enabled and the mapping is randomizable.

## Anonymous Mapping

`zmap()` validates protections and fixed-address ranges, selects an address with `choose_addr()`, and creates anonymous zero-fill mappings through `segvn_create` with a null vnode and amp.

## File Mapping

`smmap_common()` validates mmap flags, protections, file descriptor access, file offsets, fixed-address bounds, low-32-bit constraints, `MAP_TEXT` and `MAP_INITDATA` combinations, and `VFS_NOEXEC`.

For regular files it checks large-file overflow. Shared mappings require write access for writable protections. Mappings on noexec files remove executable max protection.

Before mapping a file with read/write/exec access, it enters NBMAND critical state if needed, asks `nbl_svmand()` for SVMAND behavior, and calls `nbl_conflict()` over the full mapping range. A conflict returns `EACCES`.

The actual mapping is delegated to `VOP_MAP()`. Successful shared mappings notify machine-specific shared-address-space code. Successful text/initdata regular-file mappings set `VVMEXEC` on the vnode.

## Unmap, Protect, And Residency

`munmap()` validates page alignment and user range, removes lwpchan mappings, and calls `as_unmap()`.

`mprotect()` validates address, length, and protections, then calls `as_setprot()`.

`mincore()` validates user range, walks the address interval in `MC_QUANTUM` chunks, calls `as_incore()`, and copies residency bytes back to user space.

## Important Invariants

- Heap and stack growth are serialized by `as_rangelock()`.
- Heap and stack large-page policies never deliberately reduce the selected page-size code.
- Fixed mappings unmap the target range before remapping.
- `MAP_FIXED` and `_MAP_RANDOMIZE` are rejected together.
- File mappings respect `VFS_NOEXEC`, descriptor access mode, regular-file offset overflow, and mandatory lock conflicts.
- lwpchan mappings are discarded on fixed mmap and munmap.

## Research Relevance

This file is central to filesystem/VFS research because it is the syscall-level bridge between files and virtual memory. The `VOP_MAP()` call path, `VVMEXEC` marking, noexec enforcement, and NBMAND conflict checks define how filesystem vnodes become memory mappings and how locking can block mappings.
