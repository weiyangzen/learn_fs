# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_to_text_nfs4.c

Formats NFSv4 ACLs into text. Each entry is rendered as who, access mask, flags, entry type, and optionally numeric id suffix. The formatter supports owner/group/everyone special principals and named users/groups.

Important helpers:
- `format_who()` maps ACL tags to `owner@`, `group@`, `everyone@`, `user:<name|id>`, or `group:<name|id>`.
- `format_entry_type()` maps allow/deny/audit/alarm entry types.
- `format_entry()` combines principal, `_nfs4_format_access_mask()`, `_nfs4_format_flags()`, and type.
- `_nfs4_acl_to_text_np()` iterates entries and returns a malloced string.

Flags include `ACL_TEXT_NUMERIC_IDS`, `ACL_TEXT_VERBOSE`, and `ACL_TEXT_APPEND_ID`. Name lookup uses `getpwuid()`/`getgrgid()` and is explicitly noted as thread-unsafe. Formatting assumes each entry fits within `MAX_ENTRY_LENGTH` and asserts against truncation.
