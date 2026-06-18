# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/login_access.c

Read completely: 254 lines.

This implements a `/etc/login.access` parser based on Wietse Venema’s access control logic. `login_access(user, from)` reads the file one line at a time, skips comments and blanks, requires three colon-separated fields, and stops at the first rule whose user list and origin list both match. A `+` rule grants access, a `-` rule denies access, and a missing file means no access control.

List matching supports comma/space/tab-separated tokens and `EXCEPT` clauses. User tokens support `ALL`, exact username matches, local Unix group membership, and netgroup syntax. Origin tokens support `ALL`, exact matches, domain suffixes beginning with `.`, `LOCAL` for names without dots, and network prefixes ending in `.`.

Netgroup support is stubbed out: `netgroup_match` logs that NIS netgroup support is not configured and returns no match.

Security/reliability notes: malformed lines are logged and ignored, which can accidentally broaden access if an intended deny rule is invalid. Matching uses `strtok`, so parsing is destructive and not thread-safe on shared input, but this function uses a local line buffer.
