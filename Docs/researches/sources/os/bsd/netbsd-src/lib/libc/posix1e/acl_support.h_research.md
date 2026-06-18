# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support.h

Internal header for libc POSIX.1e/NFSv4 ACL support. It declares shared helpers for ACL branding, validation, formatting, parsing, name/id conversion, NFSv4 text conversion, POSIX permission conversion, and whitespace trimming.

This header is the coordination point between `acl_strip.c`, `acl_support.c`, `acl_support_nfs4.c`, `acl_to_text.c`, `acl_to_text_nfs4.c`, `acl_valid.c`, and other ACL source files in the same directory. It also defines `_POSIX1E_ACL_STRING_PERM_MAXSIZE` as `3` for `rwx` text buffers.

Because these declarations are internal to libc, they expose implementation details such as ACL brand state and text parser heuristics rather than public API contracts.
