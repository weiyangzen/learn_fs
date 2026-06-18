# File Research: sources/os/linux/linux/fs/ocfs2/cluster/masklog.h

OCFS2 cluster logging mask header.

Defines:
- 64-bit mask constants for cluster subsystems and high-priority error/notice/kthread messages.
- Initial allow mask: `ML_ERROR | ML_NOTICE`.
- Compile-time filtering via `CONFIG_OCFS2_DEBUG_MASKLOG`; without it, only error and notice masks survive the inline test.
- `struct mlog_bits` and architecture-specific helpers for 32-bit and 64-bit `unsigned long`.

Macros:
- `mlog(mask, fmt, ...)`: fast-path mask test, then calls `__mlog_printk()`.
- `mlog_ratelimited()`: local ratelimit wrapper around `mlog`.
- `mlog_errno(st)`: logs most unexpected negative statuses but suppresses common control-flow errors.
- `mlog_bug_on_msg()`: logs condition and message before `BUG()`.

Declares:
- Global allow/deny masks.
- `__mlog_printk()`.
- Sysfs init/shutdown functions.

Operational notes:
- New mask flags must be added to both this header and `masklog.c`.
- `MLOG_MASK_PREFIX` lets files assign a subsystem prefix before including this header.
