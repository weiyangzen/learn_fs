# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_flag.c

NFSv4 ACL flag-set operations. The helper `_flag_is_invalid()` rejects flags outside `ACL_FLAGS_BITS`.

`acl_add_flag_np()`, `acl_clear_flags_np()`, `acl_delete_flag_np()`, and `acl_get_flag_np()` mutate or query raw flag sets. `acl_get_flagset_np()` and `acl_set_flagset_np()` operate on an ACL entry’s `ae_flags` and require that the entry may be NFSv4-branded; setting the flagset brands the entry as NFSv4.
