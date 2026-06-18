# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_to_text.c

Implements `acl_to_text()` and `acl_to_text_np()`. It dispatches by ACL brand: POSIX ACLs are formatted locally, NFSv4 ACLs are delegated to `_nfs4_acl_to_text_np()`.

The POSIX formatter emits lines such as `user::rwx`, `user:name:r--`, `group::r-x`, `mask::r--`, and `other::---`. It computes effective permissions for named users, group owner, and named groups by applying the mask when present, adding `# effective:` comments when the effective bits differ.

Dependencies include `_posix1e_acl_perm_to_string()`, `_posix1e_acl_id_to_name()`, `acl_support.h`, `asprintf()`, and ACL brand detection. Unknown tags or bad brands return `EINVAL`. The implementation repeatedly rebuilds the output string with `asprintf()`, favoring simplicity over allocation efficiency.
