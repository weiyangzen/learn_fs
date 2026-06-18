# File Research: sources/os/bsd/netbsd-src/sys/sys/quotactl.h

## Purpose
Defines NetBSD internal quota control command ABI used by libquota and the kernel.

## Main API
- Name length: `QUOTA_NAMELEN`.
- Status structures: `struct quotastat`, `struct quotaidtypestat`, `struct quotaobjtypestat`.
- Cursor structure: `struct quotakcursor`.
- Commands: `QUOTACTL_STAT`, `IDTYPESTAT`, `OBJTYPESTAT`, `GET`, `PUT`, `DEL`, cursor open/close/skip/get/atend/rewind, `QUOTAON`, `QUOTAOFF`.
- Argument union: `struct quotactl_args`.
- Userland internal call: `__quotactl`.

## Dependencies
Includes `sys/stdint.h` and refers to quota key/value types expected from `quota.h` users.

## Risks and Notes
The header explicitly says application code should use `<quota.h>` instead. `quotakcursor` is semi-opaque but copied in/out on each cursor operation, so its fixed size is ABI-sensitive.
