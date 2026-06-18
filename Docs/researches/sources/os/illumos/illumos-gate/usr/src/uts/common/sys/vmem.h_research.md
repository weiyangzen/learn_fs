# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmem.h

## Role

`vmem.h` defines the public interface to the illumos vmem resource allocator. Vmem arenas manage address ranges or other quantum-based resources and can import from parent arenas.

## Key Interfaces

Allocation flags include sleep/no-sleep/panic behavior compatible with `KM_*`, fit policy flags (`VM_BESTFIT`, `VM_FIRSTFIT`, `VM_NEXTFIT`), and special flags such as `VM_MEMLOAD`, `VM_NORELOC`, `VM_ABORT`, and `VM_ENDALLOC`.

Arena-creation flags include:
- `VMC_POPULATOR`
- `VMC_NO_QCACHE`
- `VMC_IDENTIFIER`
- `VMC_XALLOC`
- `VMC_XALIGN`
- `VMC_DUMPSAFE`

Segment type flags support walking allocated/free segments and private span/rotor/walker segment types.

Public types include opaque `vmem_t`, import/free callback types, and alternate `vmem_ximport_t`.

Public functions include:
- `vmem_create()` / `vmem_xcreate()`
- `vmem_destroy()`
- `vmem_alloc()` / `vmem_xalloc()`
- `vmem_free()` / `vmem_xfree()`
- `vmem_add()`
- `vmem_contains()`
- `vmem_walk()`
- `vmem_size()`
- `vmem_qcache_reap()`

Kernel-only helpers include `vmem_init()`, `vmem_update()`, `vmem_is_populator()`, and `vmem_seg_size`.

## Research Notes

`VMEM_REENTRANT` affects locking during `vmem_walk()` callbacks: the arena lock may be dropped, so callbacks must tolerate concurrent arena mutation.
