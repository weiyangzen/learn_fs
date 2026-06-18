# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_copy.c

Implements `acl_copy_entry()`. It rejects null or identical source/destination entries, ensures the destination can take the source entry’s ACL brand, brands it accordingly, and copies tag, id, permissions, entry type, and flags.

`acl_copy_ext()` and `acl_copy_int()` are present but unimplemented, returning `ENOSYS`.
