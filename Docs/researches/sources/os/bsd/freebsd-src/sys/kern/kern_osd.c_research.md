# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_osd.c

Read completely: 443 lines.

## Purpose
Implements Object Specific Data (OSD), a slot-based extension mechanism that lets kernel subsystems attach typed private data and methods to core objects without changing their structure layout.

## Main Elements
- `struct osd_master` tracks per-type module locks, object locks, object lists, destructors, methods, slot counts, and method counts.
- `osdm[]` defines OSD domains, currently with jail-specific method count metadata.
- `osd_register()` allocates or reuses a slot, installs a destructor and optional methods, and expands arrays when needed.
- `osd_deregister()` deletes all data for a slot from every object, then marks the slot unused.
- `osd_reserve()`, `osd_set()`, `osd_set_reserved()`, and `osd_free_reserved()` support normal and preallocated slot-array updates.
- `osd_get()` and `osd_get_unlocked()` return slot values under object locking or caller-provided synchronization.
- `osd_del()` and `do_osd_del()` run destructors, clear slots, shrink arrays, and remove objects from the active OSD list when empty.
- `osd_call()` invokes registered methods for a type/method across occupied slots until an error occurs.
- `osd_exit()` destroys all OSD attached to an object during object teardown.
- `osd_init()` initializes locks and lists at `SI_SUB_LOCK`.

## Dependencies And Integration
Uses sx locks for module registration, rmlocks for object slot access, mutexes for global object lists, malloc/realloc, jail method constants, sysctl debug control, and OSD public interfaces from `sys/osd.h`.

## Risk Notes
Slot registration/deregistration crosses module-level and object-level locks and can call destructors while walking all live objects. Reserved arrays avoid allocation failure in some set paths, but non-reserved growth uses `M_NOWAIT` and can fail. Deregistration leaves arrays allocated for reuse rather than shrinking global slot metadata.
