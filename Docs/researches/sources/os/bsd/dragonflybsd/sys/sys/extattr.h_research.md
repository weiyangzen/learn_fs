# File Research: sources/os/bsd/dragonflybsd/sys/sys/extattr.h

`extattr.h` defines extended filesystem attribute namespaces and the userland extended-attribute syscall API. It defines empty, user, and system namespaces with string names and an initializer macro for namespace-name tables.

Under `_KERNEL`, it defines `EXTATTR_MAXNAMELEN` and forward-declares kernel types. In userland, it declares `extattrctl()`, fd/file/link variants for delete/get/list/set operations, and related types.

This header is the public ABI for TrustedBSD-style extended attributes on DragonFly.
