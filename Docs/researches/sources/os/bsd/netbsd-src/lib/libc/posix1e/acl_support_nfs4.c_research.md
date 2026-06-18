# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support_nfs4.c

Provides NFSv4 ACL flag and access-mask formatting/parsing helpers. It maps bit values to verbose names and compact one-character forms for inheritance/audit flags and NFSv4 access permissions.

Important functions:
- `_nfs4_format_flags()` and `_nfs4_format_access_mask()` output either verbose slash-separated names or compact character fields.
- `_nfs4_parse_flags()` and `_nfs4_parse_access_mask()` first try verbose parsing and fall back to compact parsing if no verbose token matched.
- Shared static helpers implement flag scanning and parse diagnostics.

The access-mask table includes individual permissions plus aggregate set constants such as `ACL_FULL_SET`, `ACL_MODIFY_SET`, `ACL_READ_SET`, and `ACL_WRITE_SET`. Parse errors use `warnx()` with field-specific messages and return `-1`, while parsed bitsets are still assigned through output parameters.
