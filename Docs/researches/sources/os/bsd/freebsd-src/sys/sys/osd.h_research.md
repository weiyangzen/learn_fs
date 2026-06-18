# File Research: sources/os/bsd/freebsd-src/sys/sys/osd.h

This header defines object-specific data slots for kernel objects. `struct osd` stores a slot count, slot pointer array, and list linkage. Comments document locking domains: container object lock and/or `osd_object_lock` for slot state, and `osd_list_lock` for global list linkage.

Kernel APIs allow subsystems to register a slot for an object type with optional destructor and method table, deregister it, reserve storage, set/get/delete values, call registered methods, and clean up all data on object exit. Defined object classes are thread, jail, and khelp, with convenience macros wrapping the generic API for thread and jail storage.

The thread delete macro asserts the target is `curthread`, reflecting lifecycle assumptions around thread OSD mutation. Filesystem relevance is indirect: OSD is an extensibility mechanism for kernel subsystems, allowing modules and policies to associate private state with long-lived core objects without growing those structures for every optional feature.
