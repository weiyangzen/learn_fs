# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_from_text.c

Text-to-ACL parser for POSIX.1e and NFSv4 forms. `acl_from_text()` duplicates the input, initializes an ACL, strips comments, splits entries by comma/newline, auto-detects NFSv4 versus POSIX by counting separators, brands the ACL, and dispatches each entry to the appropriate parser.

The POSIX parser expects `tag:qualifier:permission`, maps user/group/mask/other tags, resolves user/group names or numeric ids through `_acl_name_to_id()`, converts permissions with `_posix1e_acl_string_to_perm()`, and appends entries with `_posix1e_acl_add_entry()`.

Validation with `acl_valid()` is present but disabled, so successful parsing can return ACLs without final validity checking.
