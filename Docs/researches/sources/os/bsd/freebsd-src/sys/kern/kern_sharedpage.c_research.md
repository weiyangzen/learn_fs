# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sharedpage.c

Read completely: 391 lines.

## Purpose
Initializes and manages the kernel-populated user shared page used for signal trampoline/VDSO data, fast userspace timekeeping, and optional FXRNG seed generation metadata.

## Main Elements
- Creates a one-page physical VM object at exec SYSINIT time, grabs and validates its page, maps it into kernel virtual address space, and exposes `shared_page_mapping`.
- Serializes allocations from the page with `shared_page_alloc_sx`, `shared_page_alloc_locked()`, `shared_page_alloc()`, and `shared_page_fill()`.
- `shared_page_write()` copies kernel data into the shared page at an allocated offset.
- `timehands_update()` writes native `vdso_timehands` data into a rotating slot, uses generation counters and release fences for lockless readers, updates the current slot, and records whether VDSO timekeeping is enabled.
- `timehands_update32()` mirrors the same scheme for 32-bit compatibility when `COMPAT_FREEBSD32` is enabled.
- Maintains singleton native and compat32 `struct vdso_sv_tk` pointers so hardclock-context `timekeep_push_vdso()` can update shared-page timekeeping without iterating sysentvec lists.
- `alloc_sv_tk()` and `alloc_sv_tk_compat32()` allocate shared-page timekeep regions, write VDSO timekeep version fields, and trigger an initial push.
- Optional `RANDOM_FENESTRASX` support allocates a cache-line-aligned shared-page FXRNG generation record and updates its 32-bit generation with release ordering via `fxrng_push_seed_generation()`.
- `exec_sysvec_init()` initializes a sysentvec's shared-page object, copies signal trampoline or VDSO signal code, registers native/compat32 timekeeping offsets, and assigns optional FXRNG generation offsets.
- `exec_sysvec_init_secondary()` copies initialized shared-page offsets and objects from a primary sysentvec to a secondary ABI-compatible sysentvec.

## Dependencies And Integration
Depends on VM pager/object/page primitives, kernel virtual mapping, pmap quick mappings, sysentvec ABI metadata, VDSO timecounter filling, exec initialization order, optional compat32 ABI support, and optional random/Fenestra SX support.

## Risk Notes
The shared page is size-limited and allocation failures are treated as panics for required ABI data. Lockless userspace timekeeping depends on generation-counter ordering and release fences. Singleton native/compat32 registration assumes sysentvec initialization order and ABI compatibility are correct.
