<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/seusers.c -->
# sources/security-integrity/selinux/libselinux/src/seusers.c

## Purpose
Maps Linux login users and services to SELinux users and MLS levels using `seusers` and per-login policy files.

## Important APIs, Types, And Functions
`process_seusers()` parses `linuxuser:seuser[:level]` records. `getseuserbyname()` resolves exact, group (`%group`), `__default__`, or username fallback mappings. `getseuser()` first tries `<policyroot>/logins/<username>` service-specific records, then falls back to `getseuserbyname()`.

## Control Flow
`getseuserbyname()` scans all records, preserving the first matching group and default while allowing exact user matches to win. Group membership is checked with `get_default_gid()`, `getgrnam_r()`, and `getgrouplist()`. MLS level parsing is skipped when MLS is disabled.

## State And Persistence Behavior
Global `require_seusers` controls whether no-match fallback to Linux username is allowed. The module reads policy config files and allocates returned strings.

## Dependencies And Integration Points
Uses config path accessors, context/MLS checks, libc passwd/group APIs, and logging callbacks for bad records.

## Risks And Test Signals
Risks include ambiguous precedence, ERANGE buffer growth, missing groups/users, malformed line handling, global `require_seusers`, and service-specific fallback. Tests should cover exact/group/default/no-match, MLS on/off, invalid records, long NSS entries, and `REQUIRESEUSERS` behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/seusers.c -->
