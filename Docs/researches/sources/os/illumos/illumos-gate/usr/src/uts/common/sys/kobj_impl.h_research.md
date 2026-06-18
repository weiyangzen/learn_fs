# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj_impl.h

## Purpose
Defines implementation-private interfaces for the kernel runtime linker/loader, including boot auxiliary attributes, module flags, notification hooks, allocation flags, early-boot vector overrides, and relocation/export routines.

## Main Interfaces
- Boot attribute constants:
  - `BA_DYNAMIC` through `BA_NUM`
- `val_t`: boot auxiliary value/pointer union.
- `struct proginfo`: segment size/alignment descriptor.
- Module flags:
  - `KOBJ_EXEC`
  - `KOBJ_INTERP`
  - `KOBJ_PRIM`
  - `KOBJ_RESOLVED`
  - `KOBJ_RELOCATED`
  - `KOBJ_NOPARENTS`
  - `KOBJ_IGNMULDEF`
  - `KOBJ_NOKSYMS`
  - `KOBJ_EXPORTED`
- Notification support:
  - `kobj_notify_f`
  - `kobj_notify_list_t`
  - `KOBJ_NOTIFY_MODLOADING`
  - `KOBJ_NOTIFY_MODUNLOADING`
  - `KOBJ_NOTIFY_MODLOADED`
  - `KOBJ_NOTIFY_MODUNLOADED`
- Allocation flags:
  - `KM_WAIT`
  - `KM_NOWAIT`
  - `KM_TMP`
  - `KM_SCRATCH`
- Core functions:
  - `kobj_init()`
  - `kobj_notify_add()`
  - `kobj_notify_remove()`
  - `do_relocations()`
  - `do_relocate()`
  - `kobj_mod_alloc()`
  - `kobj_hash_name()`
  - `kobj_segbrk()`
  - `kobj_lookup_kernel()`
  - `kobj_export_module()`
  - `kobj_load_primary_module()`
  - link-map helpers `kobj_lm_append()`, `kobj_lm_lookup()`, `kobj_lm_dump()`

## Dependencies And Relationships
Includes `sys/kdi.h`, `sys/kobj.h`, and varargs support. It exposes early boot hooks, bootops, kmdb argv, kernel debugger interface data, and standalone vector setup/restore.

## Research Notes
Under `KOBJ_OVERRIDES`, early kobj code redirects `bcopy`, `bzero`, and `strlcat` to kobj-managed function pointers until the kernel is fully linked. `KOBJ_LM_PRIMARY` and `KOBJ_LM_DEBUGGER` distinguish primary and debugger link maps.
