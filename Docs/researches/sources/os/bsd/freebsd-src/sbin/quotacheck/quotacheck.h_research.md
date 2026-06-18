# File Research: sources/os/bsd/freebsd-src/sbin/quotacheck/quotacheck.h

Shared declarations for `quotacheck`.

Key elements:
- Declares `blockcheck`, `checkfstab`, and `chkquota`.

Dependencies:
- `chkquota` uses `struct quotafile *`, so consumers must include quota definitions before or alongside this header.
