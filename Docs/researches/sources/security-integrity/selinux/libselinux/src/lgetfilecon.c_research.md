# sources/security-integrity/selinux/libselinux/src/lgetfilecon.c

Purpose: Reads a path's SELinux file context xattr without following symlinks.

Important APIs/types/functions: `lgetfilecon_raw()` uses `lgetxattr()` for `security.selinux`; `lgetfilecon()` translates the raw context.

Control flow: mirrors `getfilecon_raw()` with initial buffer, `ERANGE` resize, empty xattr mapped to `ENOTSUP`, and translated length return in the public wrapper.

State and persistence: read-only xattr access.

Dependencies and integration: used for symlink-aware labeling tools where the link's own label matters.

Risks and test signals: tests should cover symlink vs target behavior, ERANGE, empty xattr, missing xattr, and translation failure cleanup.
