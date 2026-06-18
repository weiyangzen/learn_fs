# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_mutex_obj.c

## Purpose
Provides dynamically allocated, reference-counted mutex objects aligned to cache coherency units.

## Main Interfaces
- `mutex_obj_alloc(type, ipl)`: sleeping allocation and mutex initialization.
- `mutex_obj_tryalloc(type, ipl)`: non-sleeping allocation variant.
- `mutex_obj_hold(lock)`: increments object reference count.
- `mutex_obj_free(lock)`: decrements reference count, destroys and frees object when it reaches zero, and returns whether it freed.
- `mutex_obj_refcnt(lock)`: returns current reference count.

## Internal State And Dependencies
- `struct kmutexobj` embeds `kmutex_t`, magic value `MUTEX_OBJ_MAGIC`, reference count, and cacheline padding.
- Uses `kmem_intr_alloc/free`, `_mutex_init`, `mutex_destroy`, atomic increments/decrements, and release/acquire barriers.

## Control Flow Notes
- Allocation initializes refcount to one and returns the embedded mutex address as the object handle.
- Free path uses `membar_release` before atomic decrement and `membar_acquire` before destruction on last reference.

## Risk Areas
- Refcount operations assume callers already hold a valid reference across `mutex_obj_hold`.
- `mutex_obj_refcnt` returns a raw non-atomic value and is observational only.
- Object layout assumes `kmutex_t` is at offset zero so a `kmutex_t *` can be cast back.

## Filesystem Relevance
Indirect. Useful wherever kernel subsystems need dynamically shared locks, including possible filesystem objects.
