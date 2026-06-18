# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_delete_entry.c

Entry deletion helpers for ACL objects. `acl_delete_entry()` validates ACL and entry brands, copies the target entry, removes every matching entry, shifts later entries down, clears the unused slot, and resets the cursor.

Matching is brand-sensitive: NFSv4 entries compare tag and entry type, plus id for user/group entries; POSIX-style entries compare tag and id. `acl_delete_entry_np()` deletes a specific offset with similar shifting and cursor reset.
