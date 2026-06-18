# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_rwlock_obj.c

## Purpose

`kern_rwlock_obj.c` implements dynamically allocated, reference-counted rwlock objects. These are cacheline-aligned objects embedding a `krwlock_t`, magic value, and reference count.

## Data Structure

- `struct krwobj`
  - `ro_lock`: embedded rwlock.
  - `ro_magic`: validates object identity with `RW_OBJ_MAGIC`.
  - `ro_refcnt`: object reference count.
  - padding to `COHERENCY_UNIT`.

## Functions

- `rw_obj_alloc()`
  - Allocates with `kmem_intr_alloc(..., KM_SLEEP)`.
  - Asserts cacheline alignment.
  - Initializes embedded rwlock.
  - Sets magic and refcount 1.
- `rw_obj_tryalloc()`
  - Same as allocation, but uses `KM_NOSLEEP`.
  - Returns NULL on allocation failure.
- `rw_obj_hold()`
  - Validates magic/refcount and atomically increments reference count.
- `rw_obj_free()`
  - Drops a reference with release/acquire memory barriers.
  - If references remain, returns false.
  - On last reference, destroys embedded rwlock and frees object, returning true.
- `rw_obj_refcnt()`
  - Returns current reference count without extra locking.

## Notes

This file is a small lifetime-management wrapper around `kern_rwlock.c` locks, useful when a subsystem needs a separately allocated lock object that can outlive individual references.
