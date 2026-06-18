# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_memio.c

## Purpose

`kern_memio.c` implements DragonFlyBSD's memory special devices and related ioctls: `/dev/mem`, `/dev/kmem`, `/dev/null`, `/dev/random`, `/dev/urandom`, `/dev/upmap`, `/dev/kpmap`, `/dev/lpmap`, `/dev/zero`, and `/dev/io`.

## Main Responsibilities

- Defines memory-device `dev_ops` variants for normal, memory, and non-quick devices.
- Enforces open-time privilege and securelevel checks for memory and I/O devices.
- Implements read/write behavior for physical memory, kernel memory, null, random, urandom, and zero devices.
- Implements user-kernel mapping support through `d_uksmap`.
- Implements memory range attribute ioctls through `mem_range_softc`.
- Implements random interrupt registration ioctls.
- Implements kqueue readiness filters.
- Creates all memory special devices at driver init.

## Device Behavior

`/dev/mem` maps the requested physical page into `ptvmmap`, performs `uiomove()`, and unmaps it. `/dev/kmem` checks mapped kernel address access with `kvm_access_check()` before moving directly to or from the kernel virtual address. `/dev/null` returns EOF on read and discards writes. `/dev/zero` returns zero-filled data and discards writes. `/dev/random` reads from `read_random(..., 0)` and permits seeding only when `kern.seedenable` is set and securelevel allows it. `/dev/urandom` reads with nonblocking random semantics and disallows writes.

`/dev/io` raises and clears I/O privilege level on open/close, and is blocked when securelevel is raised or kernel memory is read-only.

## Mapping Support

`memuksmap()` handles `UKSMAPOP_ADD`, `UKSMAPOP_REM`, and `UKSMAPOP_FAULT`. It tracks `/dev/lpmap` mappings on the owning LWP's `lwp_lpmap_backing_list`. Faults for `/dev/mem` map physical pages directly; `/dev/kmem` resolves kernel virtual addresses with `vtophys()`; `/dev/upmap`, `/dev/kpmap`, and `/dev/lpmap` delegate to `user_kernel_mapping()`.

`user_kernel_mapping()` creates or locates shared process, global kernel, or LWP mapping pages and returns their physical address. `/dev/upmap` has special `vfork()` handling: a child sharing the parent's pmap maps the parent's `p_upmap` and marks `invfork`.

## Ioctl and Event Notes

`mmioctl()` serializes ioctls with `mem_lock`. `MEMRANGE_GET` and `MEMRANGE_SET` copy descriptors through `mem_range_attr_get()` and `mem_range_attr_set()`. Random ioctls can register, unregister, or find interrupt randomness sources after restricted-root capability checks. Kqueue filters report memory devices as readable/writable, while `/dev/random` uses the random subsystem's read filter.
