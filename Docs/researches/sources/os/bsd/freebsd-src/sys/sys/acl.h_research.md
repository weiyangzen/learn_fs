# File Research: sources/os/bsd/freebsd-src/sys/sys/acl.h

POSIX.1e and NFSv4 access control list ABI/API header.

Key elements:
- Defines ACL scalar typedefs, maximum entry count, tags, entry types, ACL types, permissions, flag bits, text flags, and mode override/preserve masks.
- Under kernel/private builds, defines old and current ACL entry/layout structures, including `struct oldacl`, `struct acl_entry`, `struct acl`, and libc-private `struct acl_t_struct`.
- Declares kernel ACL conversion, allocation, validation, NFSv4 inheritance/sync, and old/new ACL copy helpers.
- In userland, declares POSIX.1e and FreeBSD `_np` ACL APIs; private mode also declares raw syscall interfaces.

Dependencies:
- Includes `sys/types.h` and `sys/_null.h`; kernel includes `sys/malloc.h`.

Research notes:
- Central filesystem permission metadata header.
- Comments preserve compatibility constraints for old POSIX.1e on-disk layout and 4 KiB current ACL allocation sizing.
