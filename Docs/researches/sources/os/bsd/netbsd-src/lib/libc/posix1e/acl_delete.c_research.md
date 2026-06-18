# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_delete.c

Thin deletion wrappers for file, link, and fd ACL removal. `acl_delete_def_file()` and `acl_delete_def_link_np()` delete default ACLs, while `acl_delete_file_np()`, `acl_delete_link_np()`, and `acl_delete_fd_np()` normalize old ACL type values with `_acl_type_unold()` and call the corresponding internal syscall wrapper.

No ACL parsing or validation is performed in this file.
