# sources/security-integrity/selinux/libsepol/src/user_record.c

## Purpose
`user_record.c` implements opaque high-level SELinux user records and keys, including names, MLS default level/range strings, and role-name arrays.

## Important APIs and State
`struct sepol_user` owns `name`, `mls_level`, `mls_range`, `roles`, and `num_roles`. `struct sepol_user_key` owns a name. APIs create/unpack/extract/free keys; compare records by name; get/set name and MLS strings; add/test/set/get/delete roles; and create/clone/free records.

## Control Flow and Integration
Setters deep-copy strings. `sepol_user_add_role()` is idempotent and grows the array with `reallocarray()`. `sepol_user_set_roles()` copies a complete replacement array before swapping. `sepol_user_get_roles()` returns a newly allocated array of borrowed role string pointers. `users.c` converts these records into `user_datum_t` entries.

## Risks and Test Signals
`sepol_user_del_role()` compacts by moving the last role and does not shrink allocation. MLS strings are not parsed here; validation is deferred. Tests should cover clone independence, role add/delete/set/get ownership, MLS setters, and key extraction.
