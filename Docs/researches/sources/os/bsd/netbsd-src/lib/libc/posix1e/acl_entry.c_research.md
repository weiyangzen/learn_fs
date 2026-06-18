# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_entry.c

ACL entry creation and iteration. `acl_create_entry()` appends a blank undefined entry if capacity allows, initializes tag/id/permissions/type/flags, and resets the ACL cursor.

`acl_create_entry_np()` inserts at a requested offset by shifting existing entries upward. `acl_get_entry()` supports `ACL_FIRST_ENTRY` and `ACL_NEXT_ENTRY`, returning `1` for an entry, `0` at end, and `-1` for invalid requests.
