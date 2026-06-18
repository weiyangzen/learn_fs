# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_perm.c

Permission-set operations for POSIX.1e and NFSv4 ACL bits. `_perm_is_invalid()` accepts only a single permission bit that belongs to the union of POSIX.1e and NFSv4 permission masks.

`acl_add_perm()`, `acl_clear_perms()`, `acl_delete_perm()`, and `acl_get_perm_np()` validate arguments, mutate/query the bitset, and set `EINVAL` for invalid permission values.
