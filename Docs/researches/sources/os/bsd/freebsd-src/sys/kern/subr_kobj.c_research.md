# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_kobj.c

## Purpose
Implements FreeBSD's kernel object (`kobj`) runtime support: class compilation, method lookup through base classes, object initialization, allocation, and deletion. This is an object-dispatch substrate used by multiple kernel frameworks, including device and bus abstractions.

## Main Interfaces
- `kobj_class_compile()`, `kobj_class_compile_static()`: build a class operation cache and assign method descriptor IDs.
- `kobj_lookup_method()`: resolves a method descriptor against a class and recursive base-class hierarchy, falling back to the descriptor default method.
- `kobj_create()`, `kobj_init()`, `kobj_init_static()`: allocate or initialize objects and attach compiled ops.
- `kobj_delete()`, `kobj_class_free()`: drop references and free dynamically allocated ops tables.
- `kobj_error_method()`: generic ENXIO-returning default method.

## Implementation Notes
A global mutex protects method ID allocation, class compilation, and class reference counts after normal lock initialization. Static compile/init variants are intentionally restricted to early boot before `kobj_mtx` is initialized. Classes maintain `refs`; each object initialization increments it, and deletion decrements it. Dynamic class ops are freed only when the last reference disappears.

The method cache is initialized to a `null_method` sentinel; lookup itself walks class methods and base classes rather than filling the cache in this file.

## Dependencies
Uses `sys/kobj.h`, `sys/lock.h`, `sys/mutex.h`, malloc type `M_KOBJ`, SYSINIT, and sysctls for method count and optional stats.

## Research Notes
Concurrency is centered on avoiding races between class compilation and object creation/deletion. `kobj_class_compile1()` allocates outside the lock, then rechecks under the lock. Static paths assert early boot constraints. No filesystem-specific logic appears here, but it underpins kernel object polymorphism used elsewhere in OS/device code.
