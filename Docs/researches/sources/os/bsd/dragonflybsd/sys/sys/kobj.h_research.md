# File Research: sources/os/bsd/dragonflybsd/sys/sys/kobj.h

Kernel object dispatch framework adapted from FreeBSD. It defines `kobj_t`, `kobj_class_t`, method descriptors, method tables, class fields, compiled operation caches, and macros for declaring and defining classes with zero to three base classes.

Kernel APIs instantiate/uninstantiate classes, create/init/delete objects, lookup methods with cache support, and provide default error methods. This underpins driver and bus object method dispatch rather than VFS directly, but it is part of DragonFly’s kernel module architecture.
