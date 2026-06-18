# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_get.c

ACL retrieval and accessor functions. `acl_get_file()`, `acl_get_link_np()`, and `acl_get_fd_np()` allocate an ACL with `ACL_MAX_ENTRIES`, normalize old type values, call internal kernel wrappers, set maximum count, and brand the ACL from the requested type. `acl_get_fd()` selects NFSv4 or access ACLs based on `fpathconf(fd, _PC_ACL_NFS4)`.

The accessors return permission-set pointers, allocate and return user/group qualifiers, read tag types, and read NFSv4 entry types after brand compatibility checks.
