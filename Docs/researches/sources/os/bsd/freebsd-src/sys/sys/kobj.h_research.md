# File Research: sources/os/bsd/freebsd-src/sys/sys/kobj.h

Defines FreeBSD’s kernel object method-dispatch system. It provides typedefs for objects, classes, methods, operation descriptors, and compiled operation tables.

Classes contain name, method table, object size, base classes, refs, and compiled ops. Objects begin with an ops pointer. `KOBJMETHOD`, `DEFINE_CLASS_*`, and `DECLARE_CLASS` support method-table and inheritance declarations.

Runtime APIs compile/free classes, create/init/delete objects, and perform cached method lookup through `KOBJOPLOOKUP`. The cache has 256 slots, with optional hit/miss stats. `kobj_error_method()` is the default ENXIO-like method implementation.
