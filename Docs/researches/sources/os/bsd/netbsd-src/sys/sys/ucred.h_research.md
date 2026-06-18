# File Research: sources/os/bsd/netbsd-src/sys/sys/ucred.h

Read completely: 56 lines.

Defines user-visible credential snapshot structure.

Key elements:
- Includes `syslimits.h` in kernel or `limits.h` in userland for `NGROUPS_MAX`.
- `struct uucred` stores effective uid, effective gid, group count, and group list.
- Keeps an unused compatibility field.

Risks and notes:
- Comment explicitly says userland view should not change.
- Group array size is tied to `NGROUPS_MAX`.
