# sources/security-integrity/selinux/libselinux/src/get_default_type.c

Purpose: Looks up a default SELinux type for a role from the default type configuration file.

Important APIs/types/functions: `get_default_type()` opens `selinux_default_type_path()` and calls `find_default_type()`. The helper searches for `role:` at the start of a nonblank trimmed line and duplicates the text after the colon.

Control flow: the parser reads fixed 250-byte lines with `fgets_unlocked()`, trims one trailing byte, skips leading whitespace and blank lines, and reports `EINVAL` if no matching role is found.

State and persistence: read-only configuration lookup; caller owns returned `type`.

Dependencies and integration: uses path helpers and public `selinux/get_default_type.h`.

Risks and test signals: fixed buffer length can truncate long lines; matching is prefix plus colon. Tests should cover comments/whitespace, missing role, long lines, roles that are prefixes of other roles, and allocation failure.
