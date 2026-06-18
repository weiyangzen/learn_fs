## sources/security-integrity/attr/libattr/attr_copy_file.c

Purpose: copy extended attributes between pathnames without following symlinks.

`attr_copy_file` mirrors fd copy logic using `llistxattr`, `lgetxattr`, and `lsetxattr`, preserving link-object xattrs where supported. It filters via caller callback or the default permissions checker, grows buffers on `ERANGE`, and reports source/destination/name failures. State is local and freed before return. Dependencies are Linux xattr syscalls, gettext, and `error_context`. Risks are partial copies, default exclusion of ACL metadata, symlink xattr portability, and continuing after individual get/set failures. Tests should cover symlink behavior, unsupported xattrs, and custom filter callbacks.
