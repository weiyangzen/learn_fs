# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_calc_mask.c

Implementation of `acl_calc_mask()` for POSIX.1e ACLs. It validates the pointer, brands the ACL as POSIX, duplicates it, computes the union of permissions from `ACL_USER`, `ACL_GROUP`, and `ACL_GROUP_OBJ` entries, and writes that value into an existing `ACL_MASK` entry or appends a new one.

The resulting ACL is validated with `acl_valid()` before replacing the caller’s ACL contents. Capacity failures and invalid inputs set `errno` and clean up the duplicate.
